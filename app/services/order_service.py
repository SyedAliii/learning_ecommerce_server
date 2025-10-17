from app.models.cart_products import CartProducts
from app.models.product import Product
from app.models.receipt import Receipt
from app.schemas.order import GetAllOrdersResponse, OrderBaseModel, OrderStatus, OrderBaseModel, OrderConfirmResponse, OrderShippedRequest, OrderShippedResponse, OrderDeliveredRequest, OrderDeliveredResponse
from app.schemas.generic import GenericResponse
from app.models.order import Order, OrderStatus
from app.models.user import User, UserRole
from fastapi import status
from sqlalchemy.orm import Session
from app.core.exceptions.exception_main import GenericException
from typing import List
from app.core.config import settings
import smtplib
from app.tasks.email_tasks import send_email_task

class OrderService:
    def __init__(self, db: Session):
        self.db = db

    def __get_product_ids_in_cart(self, cart_id: int):
        try:
            cart_products_ids = self.db.query(CartProducts).filter(CartProducts.cart_id == cart_id).all()
            return cart_products_ids
        except Exception as e:
            raise GenericException(reason=str(e))

    def __get_subtotal(self, product_ids_in_cart: List[CartProducts]):
        try:
            subtotal = 0
            for item in product_ids_in_cart:
                product = self.db.query(Product).filter(Product.id == item.product_id).first()
                if product:
                    subtotal += product.price * item.quantity
            return subtotal
        except Exception as e:
            self.db.rollback()
            raise GenericException(reason=str(e))
        
    def __get_products_price_breakdown(self, product_ids_in_cart: List[CartProducts]):
        try:
            products_breakdown = []
            for item in product_ids_in_cart:
                product = self.db.query(Product).filter(Product.id == item.product_id).first()
                if product:
                    products_breakdown.append(
                        {
                            "title": product.title,
                            "price": product.price,
                            "quantity": item.quantity
                        }
                    )
            return products_breakdown
        except Exception as e:
            self.db.rollback()
            raise GenericException(reason=str(e))
        
    def __update_product_stock(self, product_ids_in_cart: List[CartProducts]):
        try:
            for item in product_ids_in_cart:
                product = self.db.query(Product).filter(Product.id == item.product_id).first()
                if product:
                    product.quantity -= item.quantity
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise GenericException(reason=str(e))
    
    def __check_product_stock(self, product_ids_in_cart: List[CartProducts]):
        for item in product_ids_in_cart:
            product = self.db.query(Product).filter(Product.id == item.product_id).first()
            if product:
                if product.quantity < item.quantity:
                    return False, f"Product {product.title} is out of stock or does not have enough quantity"
        return True, None

    def __generate_receipt(self, product_ids_in_cart: List[CartProducts], order: Order):
        try:
            receipt = Receipt()
            receipt.subtotal = self.__get_subtotal(product_ids_in_cart)
            receipt.tax = receipt.subtotal * 0.1
            receipt.shipping_fee = 50
            receipt.grand_total = receipt.subtotal + receipt.tax + receipt.shipping_fee
            receipt.user_id = order.user_id
            receipt.order_id = order.id
            self.db.add(receipt)
            self.db.commit()
            self.db.refresh(receipt)
            return receipt
        except Exception as e:
            self.db.rollback()
            raise GenericException(reason=str(e))
    
    def __get_order_status_string(self, status_code: int):
        if status_code == OrderStatus.PENDING:
            return "Pending"
        elif status_code == OrderStatus.CONFIRMED:
            return "Confirmed"
        elif status_code == OrderStatus.SHIPPED:
            return "Shipped"
        elif status_code == OrderStatus.DELIVERED:
            return "Delivered"
        else:
            return "Unknown"

    def __send_email(self, user: User, order_status: str, receipt: Receipt):
        try:
            cart_id = self.db.query(Order).filter(Order.id == receipt.order_id).first().cart_id
            product_ids_in_cart = self.__get_product_ids_in_cart(cart_id)
            products_breakdown = self.__get_products_price_breakdown(product_ids_in_cart)
            
            receiver_email = self.db.query(User).filter(User.id == receipt.user_id).first().email
            subject = f"Receipt for Your Order Id: {receipt.id} - Status: " + self.__get_order_status_string(order_status)
            body = "This is an auto generated receipt for your recent order.\n\n"
            for product in products_breakdown:
                body += f"Product: {product['title']}\n"
                body += f"Price: {product['price']}\n"
                body += f"Quantity: {product['quantity']}\n"
                body += "-------------------------\n"
            body += f"Subtotal: {receipt.subtotal}\n"
            body += f"Tax: {receipt.tax}\n"
            body += f"Shipping Fee: {receipt.shipping_fee}\n"
            body += f"Grand Total: {receipt.grand_total}\n\n"
            body += f"Addressed to: {user.address}\n"
            body += "\nThank you for shopping with us!"

            try:
                # print(f"Email Credentials: {settings.SENDER_EMAIL}, {settings.APP_PASSWORD}")
                send_email_task.delay(receiver_email, subject, body)
                return True, None
            except Exception as e:
                return False, str(e)
        except Exception as e:
            return False, str(e)

    def create(self, user_id: int):
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if user.active_cart_id != None:
                product_ids_in_cart = self.__get_product_ids_in_cart(user.active_cart_id)
                stock_check_result, product_stock_reason = self.__check_product_stock(product_ids_in_cart)
                if not stock_check_result:
                    raise GenericException(reason=product_stock_reason)

                order = Order()
                order.status = OrderStatus.PENDING
                order.user_id = user.id
                order.cart_id = user.active_cart_id
                self.db.add(order)
                self.db.commit()
                return GenericResponse(
                    status_code=status.HTTP_201_CREATED,
                    msg=f"Order created successfully",
                )
            else:
                self.db.rollback()
                return GenericResponse(
                        status_code=status.HTTP_204_NO_CONTENT,
                        msg=f"No Active Cart for this user"
                    )
        except GenericException as ge:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            raise GenericException(reason=str(e))
        
    def confirm(self, user_id: int):
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if user.active_cart_id == None:
                raise GenericException(reason="No active cart to confirm order")
            
            order = self.db.query(Order).filter(Order.cart_id == user.active_cart_id).first()
            order.status = OrderStatus.CONFIRMED
            product_ids_in_cart = self.__get_product_ids_in_cart(order.cart_id)
            stock_check_result, product_stock_reason = self.__check_product_stock(product_ids_in_cart)
            if stock_check_result == False:
                raise GenericException(
                    reason=product_stock_reason
                )
            else:
                user.active_cart_id = None
                self.__update_product_stock(product_ids_in_cart)
                receipt = self.__generate_receipt(product_ids_in_cart, order)
                send_email_status, reason = self.__send_email(user, order.status, receipt)
                self.db.commit()
                return OrderConfirmResponse(
                    id=receipt.id,
                    subtotal=receipt.subtotal,
                    tax=receipt.tax,
                    shipping_fee=receipt.shipping_fee,
                    grand_total=receipt.grand_total,
                    products=self.__get_products_price_breakdown(product_ids_in_cart),
                    order=order.status,
                    status_code=status.HTTP_200_OK,
                    msg=f"Order with status: {order.status} updated successfully and email sent status: {send_email_status}. Reason: {reason}",
                )
        except GenericException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            raise GenericException(reason=str(e))

    def shipped(self, req: OrderShippedRequest, user_id: int):
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if user.roles != UserRole.ADMIN:
                raise GenericException(reason="User not authorized to update order status")
            
            order = self.db.query(Order).filter(Order.user_id == req.user_id and Order.cart_id == req.cart_id).first()
            order.status = OrderStatus.SHIPPED
            product_ids_in_cart = self.__get_product_ids_in_cart(order.cart_id)
            receipt = self.db.query(Receipt).filter(Receipt.order_id == order.id).first()
            send_email_status, reason = self.__send_email(user, order.status, receipt)
            self.db.commit()
            return OrderShippedResponse(
                id=receipt.id,
                subtotal=receipt.subtotal,
                tax=receipt.tax,
                shipping_fee=receipt.shipping_fee,
                grand_total=receipt.grand_total,
                products=self.__get_products_price_breakdown(product_ids_in_cart),
                order=order.status,
                status_code=status.HTTP_200_OK,
                msg=f"Order with status: {order.status} updated successfully and email sent status: {send_email_status}. Reason: {reason}",
            )
        except GenericException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            raise GenericException(reason=str(e))
        
    def delivered(self, req: OrderDeliveredRequest, user_id: int):
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if user.roles != UserRole.ADMIN:
                raise GenericException(reason="User not authorized to update order status")
            
            order = self.db.query(Order).filter(Order.user_id == req.user_id and Order.cart_id == req.cart_id).first()
            order.status = OrderStatus.DELIVERED
            product_ids_in_cart = self.__get_product_ids_in_cart(order.cart_id)
            receipt = self.db.query(Receipt).filter(Receipt.order_id == order.id).first()
            send_email_status, reason = self.__send_email(user, order.status, receipt)
            self.db.commit()
            return OrderDeliveredResponse(
                id=receipt.id,
                subtotal=receipt.subtotal,
                tax=receipt.tax,
                shipping_fee=receipt.shipping_fee,
                grand_total=receipt.grand_total,
                products=self.__get_products_price_breakdown(product_ids_in_cart),
                order=order.status,
                status_code=status.HTTP_200_OK,
                msg=f"Order with status: {order.status} updated successfully and email sent status: {send_email_status}. Reason: {reason}",
            )
        except GenericException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            raise GenericException(reason=str(e))

    def get_all(self, user_id: int):
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if user.roles != UserRole.ADMIN:
                raise GenericException(reason="User not authorized to get all orders")
            
            orders = self.db.query(Order).all()
            if not orders:
                return GetAllOrdersResponse(
                    orders=[],
                    status_code=status.HTTP_200_OK,
                    msg="No Orders Found"
                )
            orders_list = []
            for order in orders:
                user = self.db.query(User).filter(User.id == order.user_id).first()
                if not user:
                    continue
                product_ids_in_cart = self.__get_product_ids_in_cart(order.cart_id)
                quantity = sum([item.quantity for item in product_ids_in_cart])
                products = self.db.query(Product).filter(Product.id.in_([item.product_id for item in product_ids_in_cart])).all()
                orders_list.append(
                    OrderBaseModel(
                        id=order.id,
                        user_id=order.user_id,
                        username=user.name,
                        user_email=user.email,
                        cart_id=order.cart_id,
                        total_items=quantity,
                        total_price=sum([product.price * item.quantity for product in products for item in product_ids_in_cart if product.id == item.product_id]),
                        status=order.status
                    )
                )
            return GetAllOrdersResponse(
                orders=orders_list,
                status_code=status.HTTP_200_OK,
                msg="All Orders retrieved successfully"
            )
        except GenericException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            raise GenericException(reason=str(e))