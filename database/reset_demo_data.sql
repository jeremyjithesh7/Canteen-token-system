-- CanteenOS Operational Clean Reset Script
-- Cleans transactional and operational tables while strictly preserving schema, master catalog, categories, counters, and core administrative accounts.

PRAGMA foreign_keys = OFF;

BEGIN TRANSACTION;

-- Clear user shopping carts and notifications
DELETE FROM cart_items;
DELETE FROM notifications;

-- Clear food feedback and ratings (enforce real reviews only)
DELETE FROM food_ratings;

-- Clear transactional orders, order items, and tokens
DELETE FROM order_items;
DELETE FROM tokens;
DELETE FROM payments;
DELETE FROM orders;

-- Clear financial transactions and waste logs
DELETE FROM wallet_transactions;
DELETE FROM food_waste_logs;

-- Clear AI predictions, recommendations, preferences, and overrides
DELETE FROM prediction_overrides;
DELETE FROM demand_predictions;
DELETE FROM queue_predictions;
DELETE FROM recommendations;
DELETE FROM user_preferences;
DELETE FROM refresh_tokens;

-- Clear transient test student wallets, rewards, and student accounts (role_id = 3)
DELETE FROM wallets WHERE user_id IN (SELECT id FROM users WHERE role_id = 3);
DELETE FROM user_rewards WHERE user_id IN (SELECT id FROM users WHERE role_id = 3);
DELETE FROM users WHERE role_id = 3;

-- Reset core staff and admin wallet balances and reward points to baseline
UPDATE wallets SET balance = 0.0 WHERE user_id IN (SELECT id FROM users WHERE role_id IN (1, 2));
UPDATE user_rewards SET total_points = 0, current_tier = 'Bronze' WHERE user_id IN (SELECT id FROM users WHERE role_id IN (1, 2));

COMMIT;

PRAGMA foreign_keys = ON;
