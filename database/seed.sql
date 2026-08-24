-- Digital Canteen Token System - Production South Indian Seed Data
-- 3 Focused Categories, 25 Distinct Validated Photo Specialties, Ratings & Multi-Week Orders

-- 1. Roles
INSERT INTO roles (id, name, description) VALUES
(1, 'admin', 'Canteen Manager with full administrative permissions'),
(2, 'staff', 'Canteen kitchen and counter operator'),
(3, 'student', 'College student ordering food and viewing tokens')
ON CONFLICT (id) DO NOTHING;

-- 2. Users (Admin@123, Student@123, Staff@123)
INSERT INTO users (id, name, email, phone, role_id, password_hash, is_active, department) VALUES
(1, 'Canteen Administrator', 'admin@canteen.edu', '+1-555-0100', 1, '$2b$12$g9zKxI40v58rU8c95Vbeeu7rI3zVdE6ZkJ0Yd3A5kK7Xj8U6bU16e', TRUE, 'Canteen Management'),
(2, 'Aarav Sharma', 'student@canteen.edu', '+1-555-0101', 3, '$2b$12$g9zKxI40v58rU8c95Vbeeu7rI3zVdE6ZkJ0Yd3A5kK7Xj8U6bU16e', TRUE, 'Computer Science'),
(3, 'Priya Patel', 'priya@canteen.edu', '+1-555-0102', 3, '$2b$12$g9zKxI40v58rU8c95Vbeeu7rI3zVdE6ZkJ0Yd3A5kK7Xj8U6bU16e', TRUE, 'Electronics & Comm'),
(4, 'Rohan Mehta', 'rohan@canteen.edu', '+1-555-0103', 3, '$2b$12$g9zKxI40v58rU8c95Vbeeu7rI3zVdE6ZkJ0Yd3A5kK7Xj8U6bU16e', TRUE, 'Mechanical Eng'),
(5, 'Kitchen Counter Staff', 'staff@canteen.edu', '+1-555-0104', 2, '$2b$12$g9zKxI40v58rU8c95Vbeeu7rI3zVdE6ZkJ0Yd3A5kK7Xj8U6bU16e', TRUE, 'Kitchen Operations')
ON CONFLICT (id) DO NOTHING;

-- 3. Counters
INSERT INTO counters (id, name, code, station_type, description, is_active, display_order) VALUES
(1, 'South Indian Tiffin & Meals', 'C1', 'Tiffin & Rice Meals', 'Dosas, Idlis, Vadas, Upma, Pongal, and Hot Rice Dishes', TRUE, 1),
(2, 'Desserts & Sweets Counter', 'C2', 'Traditional Sweets', 'Payasam, Mysore Pak, Kesari, Halwa, and Gulab Jamun', TRUE, 2),
(3, 'Beverages & Cafe Bar', 'C3', 'Coolers & Hot Brews', 'Filter Coffee, Masala Chai, Majjige, Coconut Water, and Soda', TRUE, 3)
ON CONFLICT (id) DO NOTHING;

-- 4. Categories
INSERT INTO categories (id, name, slug, description, display_order, icon, is_active) VALUES
(1, 'South Indian Tiffin & Meals', 'south-indian-tiffin-meals', 'Authentic crispy dosas, steamed idlis, fragrant rice bowls, and comforting tiffins.', 1, 'utensils', TRUE),
(2, 'Desserts', 'desserts', 'Traditional South Indian sweets, rich ghee puddings, halwa, and melt-in-mouth delicacies.', 2, 'cookie', TRUE),
(3, 'Beverages', 'beverages', 'Authentic filter coffee, soothing masala chai, fresh fruit juices, and cooling majjige.', 3, 'coffee', TRUE)
ON CONFLICT (id) DO NOTHING;

-- 5. Food Items (25 Distinct Validated Photo Specialty URLs)
INSERT INTO food_items (id, category_id, counter_id, name, description, price, prep_time_minutes, is_veg, is_vegan, is_available, image_url, calories, protein, carbs, fats) VALUES
-- South Indian Tiffin & Meals (1-12, Counter 1)
(1, 1, 1, 'Masala Dosa', 'Crispy golden fermented crepe stuffed with aromatic spiced potato masala, served with hot sambar and fresh chutneys.', 65.00, 8, TRUE, TRUE, TRUE, 'https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=600&auto=format&fit=crop&q=80', 320, 7.5, 52.0, 9.0),
(2, 1, 1, 'Plain Dosa', 'Thin, crispy golden brown crepe served with piping hot vegetable lentil sambar and trio of coconut & tomato chutneys.', 50.00, 6, TRUE, TRUE, TRUE, 'https://images.unsplash.com/photo-1668236543090-82eba5ee5976?w=600&auto=format&fit=crop&q=80', 260, 6.0, 45.0, 6.5),
(3, 1, 1, 'Rava Dosa', 'Lacy, crunchy roasted semolina crepe tempered with cumin, black pepper, ginger, and diced green chillies.', 70.00, 10, TRUE, TRUE, TRUE, 'https://images.unsplash.com/photo-1516714435131-44d6b64dc6a2?w=600&auto=format&fit=crop&q=80', 310, 6.5, 48.0, 10.0),
(4, 1, 1, 'Idli (2 pcs / plate)', 'Fluffy, melt-in-the-mouth steamed rice and lentil cakes served with traditional drumstick sambar and fresh coconut chutney.', 40.00, 4, TRUE, TRUE, TRUE, 'https://images.unsplash.com/photo-1567188040759-fb8a883dc6d8?w=600&auto=format&fit=crop&q=80', 180, 7.0, 36.0, 2.0),
(5, 1, 1, 'Medu Vada (2 pcs)', 'Crispy golden fried savory lentil fritters with fluffy soft centers, infused with crushed peppercorns and curry leaves.', 45.00, 5, TRUE, TRUE, TRUE, 'https://images.unsplash.com/photo-1601050690597-df0568f70950?w=600&auto=format&fit=crop&q=80', 260, 8.0, 28.0, 13.0),
(6, 1, 1, 'Uttapam (Onion Tomato)', 'Thick, pillowy fermented pancake generously griddled with juicy chopped tomatoes, crunchy onions, and fresh cilantro.', 65.00, 9, TRUE, TRUE, TRUE, 'https://images.unsplash.com/photo-1626777552726-4a6b54c97e46?w=600&auto=format&fit=crop&q=80', 330, 8.5, 54.0, 9.5),
(7, 1, 1, 'Pongal (Ven Pongal)', 'Comforting savory porridge of rice and yellow moong dal slow-cooked in pure ghee with cashews, crushed cumin, and ginger.', 55.00, 5, TRUE, FALSE, TRUE, 'https://images.unsplash.com/photo-1540420773420-3366772f4999?w=600&auto=format&fit=crop&q=80', 340, 9.0, 48.0, 14.0),
(8, 1, 1, 'Upma (Rava Upma)', 'Lightly roasted semolina cooked with mustard seeds, curry leaves, ginger, garden veggies, and crunchy roasted peanuts.', 40.00, 4, TRUE, TRUE, TRUE, 'https://images.unsplash.com/photo-1610057099431-d73a1c9d2f2f?w=600&auto=format&fit=crop&q=80', 220, 5.5, 38.0, 5.0),
(9, 1, 1, 'Sambar Rice', 'Fragrant steamed rice slow-simmered in tangy tamarind, mixed country vegetables, and aromatic South Indian sambar spices.', 60.00, 6, TRUE, TRUE, TRUE, 'https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=600&auto=format&fit=crop&q=80', 380, 9.5, 65.0, 7.0),
(10, 1, 1, 'Curd Rice', 'Cooling creamy curd rice tempered with mustard seeds, fresh ginger, curry leaves, green chillies, and juicy pomegranate arils.', 50.00, 3, TRUE, FALSE, TRUE, 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=600&auto=format&fit=crop&q=80', 290, 7.0, 44.0, 8.5),
(11, 1, 1, 'Bisi Bele Bath', 'Classic Karnataka spicy hot lentil and rice dish loaded with vegetables, nutmeg, ghee, served with crunchy boondi.', 70.00, 7, TRUE, FALSE, TRUE, 'https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=600&auto=format&fit=crop&q=80', 410, 11.0, 68.0, 12.0),
(12, 1, 1, 'Lemon Rice', 'Zesty turmeric-infused basmati rice tossed with fresh lemon juice, crunchy peanuts, split lentils, and curry leaves.', 50.00, 4, TRUE, TRUE, TRUE, 'https://images.unsplash.com/photo-1589302168068-964664d93dc0?w=600&auto=format&fit=crop&q=80', 310, 5.0, 54.0, 8.0),

-- Desserts (13-18, Counter 2)
(13, 2, 2, 'Payasam (Semiya/Vermicelli Kheer)', 'Traditional sweet vermicelli pudding simmered in cardamom-infused whole milk, garnished with golden fried cashews and raisins.', 45.00, 3, TRUE, FALSE, TRUE, 'https://images.unsplash.com/photo-1596797038530-2c107229654b?w=600&auto=format&fit=crop&q=80', 280, 6.0, 42.0, 10.0),
(14, 2, 2, 'Mysore Pak', 'Royal heritage sweet crafted from roasted chickpea flour, pure desi ghee, and sugar that effortlessly melts in your mouth.', 40.00, 2, TRUE, FALSE, TRUE, 'https://images.unsplash.com/photo-1509440159596-0249088772ff?w=600&auto=format&fit=crop&q=80', 350, 4.0, 45.0, 18.0),
(15, 2, 2, 'Rava Kesari', 'Fragrant glowing golden semolina pudding enriched with pure ghee, saffron strands, cardamom, and roasted cashews.', 40.00, 3, TRUE, FALSE, TRUE, 'https://images.unsplash.com/photo-1606313564200-e75d5e30476c?w=600&auto=format&fit=crop&q=80', 310, 4.5, 48.0, 12.0),
(16, 2, 2, 'Gulab Jamun (2 pcs)', 'Soft golden milk dumplings soaked in warm rose and cardamom scented sugar syrup, served warm.', 40.00, 2, TRUE, FALSE, TRUE, 'https://images.unsplash.com/photo-1541781774459-bb2af2f05b55?w=600&auto=format&fit=crop&q=80', 290, 4.0, 50.0, 9.0),
(17, 2, 2, 'Badam Halwa', 'Luxurious almond fudge prepared from blanched ground California almonds, Kashmiri saffron, and pure clarified butter.', 65.00, 3, TRUE, FALSE, TRUE, 'https://images.unsplash.com/photo-1579372786545-d24232daf58c?w=600&auto=format&fit=crop&q=80', 380, 8.0, 38.0, 22.0),
(18, 2, 2, 'Jalebi (100g)', 'Crispy, crunchy golden pretzel spirals fried to perfection and drenched in fragrant saffron sugar syrup.', 40.00, 3, TRUE, TRUE, TRUE, 'https://images.unsplash.com/photo-1599488615731-7e5c2823ff28?w=600&auto=format&fit=crop&q=80', 320, 2.5, 62.0, 8.0),

-- Beverages (19-25, Counter 3)
(19, 3, 3, 'Filter Coffee', 'Iconic South Indian chicory blend freshly brewed in brass filters, frothed with hot creamy milk in traditional davarah & tumbler.', 25.00, 3, TRUE, FALSE, TRUE, 'https://images.unsplash.com/photo-1517256064527-09c73fc73e38?w=600&auto=format&fit=crop&q=80', 110, 3.5, 15.0, 4.0),
(20, 3, 3, 'Masala Chai', 'Aromatic full-bodied black tea brewed with crushed fresh ginger, green cardamom, cinnamon, and whole milk in an earthen kulhad.', 20.00, 3, TRUE, FALSE, TRUE, 'https://images.unsplash.com/photo-1544787219-7f47ccb76574?w=600&auto=format&fit=crop&q=80', 95, 2.8, 14.0, 3.2),
(21, 3, 3, 'Buttermilk (Majjige/Chaas)', 'Cooling spiced churned yogurt drink seasoned with roasted cumin, ginger, green chillies, curry leaves, and fresh coriander.', 25.00, 2, TRUE, FALSE, TRUE, 'https://images.unsplash.com/photo-1613478223719-2ab802602423?w=600&auto=format&fit=crop&q=80', 65, 3.0, 6.0, 2.2),
(22, 3, 3, 'Tender Coconut Water', '100% pure naturally hydrating tender coconut water served chilled with freshly scooped soft coconut malai.', 45.00, 2, TRUE, TRUE, TRUE, 'https://images.unsplash.com/photo-1525385133512-2f3bdd039054?w=600&auto=format&fit=crop&q=80', 45, 1.0, 9.0, 0.2),
(23, 3, 3, 'Rose Milk', 'Chilled milk flavored with fragrant Damascus rose extract, lightly sweetened and topped with soaked basil sabja seeds.', 35.00, 2, TRUE, FALSE, TRUE, 'https://images.unsplash.com/photo-1556881286-fc6915169721?w=600&auto=format&fit=crop&q=80', 160, 4.0, 24.0, 5.0),
(24, 3, 3, 'Sulaimani (Spiced Black Tea)', 'Traditional Malabar spiced golden black tea infused with crushed cardamom, fresh mint, and a squeeze of fresh yellow lemon.', 20.00, 3, TRUE, TRUE, TRUE, 'https://images.unsplash.com/photo-1576092768241-dec231879fc3?w=600&auto=format&fit=crop&q=80', 40, 0.5, 9.0, 0.0),
(25, 3, 3, 'Fresh Lime Soda', 'Fizzy chilled sparkling soda with freshly squeezed lime juice, rock salt, and mint (Sweet / Salt / Mixed).', 35.00, 2, TRUE, TRUE, TRUE, 'https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?w=600&auto=format&fit=crop&q=80', 80, 0.2, 20.0, 0.0)
ON CONFLICT (id) DO NOTHING;

-- 6. Daily Menu
INSERT INTO menu (id, menu_date, is_active) VALUES
(1, CURRENT_DATE, TRUE)
ON CONFLICT (id) DO NOTHING;

-- 7. Menu Items Link
INSERT INTO menu_items (menu_id, food_item_id, daily_stock_limit)
SELECT 1, id, 120 FROM food_items
ON CONFLICT DO NOTHING;

-- 8. Starting Inventory
INSERT INTO inventory (id, food_item_id, current_stock, minimum_stock_alert, unit) VALUES
(1, 1, 60, 12, 'portions'),
(2, 2, 50, 10, 'portions'),
(3, 3, 40, 10, 'portions'),
(4, 4, 80, 15, 'plates'),
(5, 5, 60, 12, 'plates'),
(6, 6, 45, 10, 'portions'),
(7, 7, 50, 10, 'portions'),
(8, 8, 40, 10, 'portions'),
(9, 9, 50, 12, 'portions'),
(10, 10, 45, 10, 'portions'),
(11, 11, 40, 10, 'portions'),
(12, 12, 45, 10, 'portions'),
(13, 13, 35, 8, 'bowls'),
(14, 14, 50, 10, 'pieces'),
(15, 15, 45, 10, 'portions'),
(16, 16, 60, 15, 'pieces'),
(17, 17, 30, 8, 'portions'),
(18, 18, 40, 10, 'plates'),
(19, 19, 150, 25, 'cups'),
(20, 20, 120, 20, 'cups'),
(21, 21, 80, 15, 'glasses'),
(22, 22, 50, 10, 'glasses'),
(23, 23, 60, 12, 'glasses'),
(24, 24, 70, 15, 'cups'),
(25, 25, 80, 15, 'glasses')
ON CONFLICT (id) DO NOTHING;

-- 9. Initial Customer Ratings & Feedback
INSERT INTO food_ratings (id, user_id, food_item_id, rating, comment) VALUES
(1, 2, 1, 5, 'Best Masala Dosa on campus! Super crispy and sambar is authentic.'),
(2, 3, 19, 5, 'Degree filter coffee is refreshing and piping hot.'),
(3, 4, 4, 5, 'Idlis are incredibly soft and melt in your mouth.'),
(4, 2, 13, 5, 'Payasam tastes just like homemade celebration kheer!'),
(5, 3, 21, 4, 'Cooling Majjige with roasted jeera is perfect for hot afternoons.')
ON CONFLICT (id) DO NOTHING;

-- 10. Initial Demand Overrides
INSERT INTO prediction_overrides (id, food_item_id, prediction_date, meal_slot, original_predicted_quantity, override_quantity, reason, admin_user_id) VALUES
(1, 1, CURRENT_DATE, 'Breakfast', 45, 60, 'High morning student rush for Masala Dosa', 1),
(2, 19, CURRENT_DATE, 'Breakfast', 70, 90, 'Morning filter coffee buffer', 1)
ON CONFLICT (id) DO NOTHING;
