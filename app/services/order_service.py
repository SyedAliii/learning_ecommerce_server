from ..models.cart_products import CartProducts
from ..models.product import Product
from ..models.receipt import Receipt
from ..schemas.order import OrderUpdateRequest, OrderUpdateResponse
from ..schemas.generic import GenericResponse
from ..models.order import Order, OrderStatus
from ..models.user import User
from fastapi import status
from sqlalchemy.orm import Session
from ..core.exceptions.exception_main import GenericException
from typing import List
from app.core.config import settings
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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

    def __generate_receipt(self, order: Order):
        try:
            product_ids_in_cart = self.__get_product_ids_in_cart(order.cart_id)
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
            self.__update_product_stock(product_ids_in_cart)
            return receipt, product_ids_in_cart
        except Exception as e:
            self.db.rollback()
            raise GenericException(reason=str(e))
        
    def __send_email(self, receipt: Receipt):
        try:
            cart_id = self.db.query(Order).filter(Order.id == receipt.order_id).first().cart_id
            product_ids_in_cart = self.__get_product_ids_in_cart(cart_id)
            products_breakdown = self.__get_products_price_breakdown(product_ids_in_cart)
            
            sender_email = settings.SENDER_EMAIL
            receiver_email = self.db.query(User).filter(User.id == receipt.user_id).first().email
            app_password = settings.APP_PASSWORD
            
            message = MIMEMultipart()
            message["From"] = sender_email
            message["To"] = receiver_email
            message["Subject"] = "Receipt for Your Order"

            body = "This is an auto generated receipt for your recent order.\n\n"
            for product in products_breakdown:
                body += f"Product: {product['title']}\n"
                body += f"Price: {product['price']}\n"
                body += f"Quantity: {product['quantity']}\n"
                body += "-------------------------\n"
            body += f"Subtotal: {receipt.subtotal}\n"
            body += f"Tax: {receipt.tax}\n"
            body += f"Shipping Fee: {receipt.shipping_fee}\n"
            body += f"Grand Total: {receipt.grand_total}\n"
            body += "\nThank you for shopping with us!"

            message.attach(MIMEText(body, "plain"))

            try:
                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.starttls()
                server.login(sender_email, app_password)
                server.sendmail(sender_email, receiver_email, message.as_string())
                return True
            finally:
                server.quit()
        except Exception as e:
            self.db.rollback()
            raise GenericException(reason=str(e))

    def create(self, user_id: int):
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if user.active_cart_id != None:
                order = Order()
                order.status = OrderStatus.PENDING
                order.user_id = user.id
                order.cart_id = user.active_cart_id
                user.active_cart_id = None
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
        except GenericException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            raise GenericException(reason=str(e))
        
    def update(self, req: OrderUpdateRequest, user_id: int):
        try:
            order = self.db.query(Order).filter(Order.user_id == user_id).first()
            if order:
                order.status = req.status
                if order.status == OrderStatus.CONFIRMED:
                    receipt, product_ids_in_cart = self.__generate_receipt(order)
                    self.__send_email(receipt)
                    self.db.commit()
                    return OrderUpdateResponse(
                        id=receipt.id,
                        subtotal=receipt.subtotal,
                        tax=receipt.tax,
                        shipping_fee=receipt.shipping_fee,
                        grand_total=receipt.grand_total,
                        products=self.__get_products_price_breakdown(product_ids_in_cart),
                        order=order.status,
                        status_code=status.HTTP_200_OK,
                        msg=f"Order with status: {order.status} updated successfully and email sent",
                    )
                elif order.status in [OrderStatus.SHIPPED, OrderStatus.DELIVERED]:
                    product_ids_in_cart = self.__get_product_ids_in_cart(order.cart_id)
                    receipt = self.db.query(Receipt).filter(Receipt.order_id == order.id).first()
                    self.__send_email(receipt)
                    self.db.commit()
                    return OrderUpdateResponse(
                        id=receipt.id,
                        subtotal=receipt.subtotal,
                        tax=receipt.tax,
                        shipping_fee=receipt.shipping_fee,
                        grand_total=receipt.grand_total,
                        products=self.__get_products_price_breakdown(product_ids_in_cart),
                        order=order.status,
                        status_code=status.HTTP_200_OK,
                        msg=f"Order with status: {order.status} updated successfully and email sent",
                    )
                else:
                    return GenericResponse(
                        status_code=status.HTTP_200_OK,
                        msg=f"Unable to update order status because status not recognized"
                    )
            else:
                self.db.rollback()
                return GenericResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    msg=f"Order not found"
                )
        except GenericException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            raise GenericException(reason=str(e))