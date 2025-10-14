INSERT INTO categories (id) VALUES
('electronics'),
('fashion'),
('home_kitchen'),
('sports_outdoors'),
('books');

INSERT INTO subcategories (id) VALUES
('smartphones'),
('laptops'),
('mens_clothing'),
('womens_clothing'),
('kitchen_appliances'),
('furniture'),
('fitness_equipment'),
('outdoor_gear'),
('fiction_books'),
('nonfiction_books');


INSERT INTO categories_subcategories (category_id, subcategory_id) VALUES
('electronics', 'smartphones'),
('electronics', 'laptops'),

('fashion', 'mens_clothing'),
('fashion', 'womens_clothing'),

('home_kitchen', 'kitchen_appliances'),
('home_kitchen', 'furniture'),

('sports_outdoors', 'fitness_equipment'),
('sports_outdoors', 'outdoor_gear'),

('books', 'fiction_books'),
('books', 'nonfiction_books');

INSERT INTO products (id, title, description, price, quantity, category_id, subcategory_id, status) VALUES
('prod001', 'iPhone 15 Pro', 'Latest Apple smartphone with A17 chip and advanced camera system.', 1199, 25, 'electronics', 'smartphones', 'AVAILABLE'),
('prod002', 'Dell XPS 13', 'Compact and powerful laptop for professionals.', 999, 30, 'electronics', 'laptops', 'AVAILABLE'),
('prod003', 'Men’s Leather Jacket', 'Stylish and durable leather jacket for men.', 199, 40, 'fashion', 'mens_clothing', 'AVAILABLE'),
('prod004', 'Women’s Summer Dress', 'Lightweight floral dress perfect for summer.', 79, 50, 'fashion', 'womens_clothing', 'AVAILABLE'),
('prod005', 'Air Fryer Pro 5L', 'Healthy cooking made easy with a large-capacity air fryer.', 149, 20, 'home_kitchen', 'kitchen_appliances', 'AVAILABLE'),
('prod006', 'Modern Sofa Set', 'Comfortable 3-seater sofa made with high-quality fabric.', 899, 10, 'home_kitchen', 'furniture', 'AVAILABLE'),
('prod007', 'Treadmill 3000X', 'Foldable treadmill with smart features for home fitness.', 599, 15, 'sports_outdoors', 'fitness_equipment', 'AVAILABLE'),
('prod008', 'Camping Tent 4-Person', 'Durable, waterproof tent perfect for family camping trips.', 249, 18, 'sports_outdoors', 'outdoor_gear', 'AVAILABLE'),
('prod009', 'The Silent Patient', 'Thrilling psychological fiction bestseller.', 24, 100, 'books', 'fiction_books', 'AVAILABLE'),
('prod010', 'Atomic Habits', 'Bestselling self-improvement book by James Clear.', 22, 120, 'books', 'nonfiction_books', 'AVAILABLE');


INSERT INTO product_images (url, product_id) VALUES
  ('https://images.unsplash.com/photo-1690819488480?auto=format&fit=crop&w=800', 'prod001'),
  ('https://images.unsplash.com/photo-1567521463850-4939134bcd4a?auto=format&fit=crop&w=800', 'prod002'),
  ('https://plus.unsplash.com/premium_photo-1661313817350-1fa759c43a3b?auto=format&fit=crop&w=800', 'prod003'),
  ('https://images.unsplash.com/photo-1512436991641-6745cdb1723f?auto=format&fit=crop&w=800', 'prod004'),
  ('https://images.unsplash.com/photo-1586201375761-83865001e31b?auto=format&fit=crop&w=800', 'prod005'),
  ('https://images.unsplash.com/photo-1582582494700-7b5f98a86d19?auto=format&fit=crop&w=800', 'prod006'),
  ('https://images.unsplash.com/photo-1571731956672-c9a0c38b8b5b?auto=format&fit=crop&w=800', 'prod007'),
  ('https://images.unsplash.com/photo-1507504031003-b4179c8d59a1?auto=format&fit=crop&w=800', 'prod008'),
  ('https://images.unsplash.com/photo-1532012197267-da84d127e765?auto=format&fit=crop&w=800', 'prod009'),
  ('https://images.unsplash.com/photo-1553729784-e91953dec042?auto=format&fit=crop&w=800', 'prod010');


DROP TABLE products, product_images, categories, subcategories, categories_subcategories CASCADE;

DROP TABLE users, carts, cart_products, products, product_images, orders, receipts, categories, subcategories, categories_subcategories CASCADE;
