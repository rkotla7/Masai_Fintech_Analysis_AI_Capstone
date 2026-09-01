---Part 1B : SQL fraud-pattern detection


----- Q1_basic_filter_sort[SELECT / WHERE / ORDER BY / LIMIT / DISTINCT] -----
-- Distinct payment methods used for high-value (>=2999) captured transactions[recent 10],

SELECT DISTINCT payment_method, amount_inr, transaction_time
FROM transactions
WHERE status = 'captured' AND amount_inr >= 2999
ORDER BY transaction_time DESC
LIMIT 10;

[10 rows returned]
payment_method  amount_inr    transaction_time
           UPI        2999 2026-01-30 12:25:00
           UPI        4999 2026-01-30 09:20:00
        Wallet        2999 2026-01-29 11:13:00
           UPI        2999 2026-01-28 16:29:00
           UPI        4999 2026-01-26 00:05:00
           UPI        2999 2026-01-23 10:24:00
        Wallet        2999 2026-01-23 05:19:00
          Card        2999 2026-01-22 13:20:00
        Wallet        2999 2026-01-22 12:18:00
           UPI        2999 2026-01-21 04:31:00


----- Q2_[GROUP BY / HAVING] -----
-- Merchants with more than 10 transactions, ranked by total GMV.


SELECT merchant_id, COUNT(*) AS txn_count, SUM(amount_inr) AS total_gmv_inr
FROM transactions
GROUP BY merchant_id
HAVING COUNT(*) > 10
ORDER BY total_gmv_inr DESC;

[32 rows returned]
 merchant_id  txn_count  total_gmv_inr
          39         13          22687
          13         12          18388
           7         16          15934
          25         17          15533
          27         16          13584
          10         14          13086
          29         19          13081
          17         13          13037
          37         19          12931
          19         14          12836
          36         16          12534
          22         16          12534
          16         20          11130
          12         13          10387
          33         11          10339
          34         16          10034
          35         14           9286
          21         14           8886
          40         15           8735
           3         17           8233
          32         14           8086
          30         17           7883
          15         12           7838
           6         14           7436
           8         16           7434
          18         11           7089
          14         12           6488
           5         11           5839
          26         12           5188
           9         18           4982
          31         15           4835
          24         13           3587


----- Q3_INNER JOIN -----
-- Transaction detail with merchant name/category/region attached.

SELECT t.transaction_id, t.amount_inr, t.status, m.merchant_name, m.category, m.region
FROM transactions t
INNER JOIN merchants m ON t.merchant_id = m.merchant_id
ORDER BY t.transaction_id
LIMIT 10;

[10 rows returned]
transaction_id  amount_inr   status merchant_name     category region
     TXN100000        2999 captured  Merchant_016 bill_payment   West
     TXN100001          49 captured  Merchant_027    ecommerce  North
     TXN100002        1499 captured  Merchant_011    ecommerce  North
     TXN100003          49 captured  Merchant_022       travel  South
     TXN100004          99 captured  Merchant_016 bill_payment   West
     TXN100005          99 captured  Merchant_003      grocery   East
     TXN100006          99 captured  Merchant_023       travel  North
     TXN100007          99 captured  Merchant_013       travel   East
     TXN100008         799 captured  Merchant_018      grocery   West
     TXN100009         299 captured  Merchant_035     recharge   East


----- Q4_LEFT JOIN -----
-- Every user LEFT JOINed to their chargeback transactions (NULLs = users with zero chargebacks). Shown here restricted to the first 10 users by id

SELECT u.user_id, u.signup_date, t.transaction_id, t.status
FROM users u
LEFT JOIN transactions t
    ON u.user_id = t.user_id AND t.status = 'chargeback'
WHERE u.user_id <= 10
ORDER BY u.user_id;

[10 rows returned]
 user_id         signup_date transaction_id status
       1 2024-06-04 00:00:00           None   None
       2 2025-03-27 00:00:00           None   None
       3 2025-06-18 00:00:00           None   None
       4 2024-08-16 00:00:00           None   None
       5 2024-11-09 00:00:00           None   None
       6 2025-03-01 00:00:00           None   None
       7 2024-02-16 00:00:00           None   None
       8 2024-05-11 00:00:00           None   None
       9 2025-04-22 00:00:00           None   None
      10 2025-01-04 00:00:00           None   None


----- Q5_chargeback_impact -----
-- count of chargeback transactions, unique users affected, total chargeback amount.
SELECT
    COUNT(*)                         AS chargeback_txn_count,
    COUNT(DISTINCT user_id)          AS unique_users_affected,
    SUM(amount_inr)                  AS total_chargeback_amount_inr
FROM transactions
WHERE status = 'chargeback';

[1 rows returned]
 chargeback_txn_count  unique_users_affected  total_chargeback_amount_inr
                   28                     27                        54472


----- Q6_burner_accounts -----
-- Burner-account fraud: chargeback transactions where the user's account
-- was less than 30 days old at the time of the transaction.
-- Explicit unambiguous boundary: 0 <= (transaction_time - signup_date).days < 30
SELECT
    t.transaction_id,
    t.user_id,
    u.signup_date,
    t.transaction_time,
    t.amount_inr,
    CAST(julianday(t.transaction_time) - julianday(u.signup_date) AS INTEGER) AS account_age_days
FROM transactions t
INNER JOIN users u ON t.user_id = u.user_id
WHERE t.status = 'chargeback'
  AND julianday(t.transaction_time) - julianday(u.signup_date) >= 0
  AND julianday(t.transaction_time) - julianday(u.signup_date) < 30
ORDER BY t.transaction_time;

[15 rows returned]
transaction_id  user_id         signup_date    transaction_time  amount_inr  account_age_days
     TXN200001      352 2025-12-31 12:00:00 2026-01-11 12:00:00        4999                11
     TXN200009      360 2025-12-22 13:00:00 2026-01-13 13:00:00        1999                22
     TXN200004      355 2026-01-05 12:00:00 2026-01-16 12:00:00        4999                11
     TXN200014      365 2025-12-27 21:00:00 2026-01-18 21:00:00        1999                22
     TXN200010      361 2026-01-11 07:00:00 2026-01-20 07:00:00        4999                 9
     TXN200002      353 2026-01-10 14:00:00 2026-01-21 14:00:00        1999                11
     TXN200003      354 2025-12-29 19:00:00 2026-01-21 19:00:00        4999                23
     TXN200013      364 2026-01-04 22:00:00 2026-01-22 22:00:00         999                18
     TXN200011      362 2026-01-08 02:00:00 2026-01-23 02:00:00        4999                15
     TXN200006      357 2026-01-19 11:00:00 2026-01-23 11:00:00        1999                 4
     TXN200012      363 2026-01-06 17:00:00 2026-01-23 17:00:00         999                17
     TXN200008      359 2026-01-18 22:00:00 2026-01-25 22:00:00        2999                 7
     TXN200007      358 2026-01-06 05:00:00 2026-01-28 05:00:00         999                22
     TXN200005      356 2026-01-18 07:00:00 2026-01-29 07:00:00        2999                11
     TXN200000      351 2026-01-15 06:00:00 2026-01-30 06:00:00        1999                15


----- Q7_velocity_attacks -----
-- users with 3+ transactions within any rounded 10-minute bucket of transaction_time.

SELECT
    user_id,
    strftime('%Y-%m-%d %H:', transaction_time) ||
        printf('%02d', (CAST(strftime('%M', transaction_time) AS INTEGER) / 10) * 10)
        AS ten_min_bucket,
    COUNT(*) AS txns_in_bucket,
    MIN(transaction_time) AS cluster_start_time
FROM transactions
GROUP BY user_id, ten_min_bucket
HAVING COUNT(*) >= 3
ORDER BY user_id, ten_min_bucket;

[8 rows returned]
 user_id   ten_min_bucket  txns_in_bucket  cluster_start_time
      59 2026-01-09 21:00               4 2026-01-09 21:00:00
      73 2026-01-12 09:00               4 2026-01-12 09:00:00
     154 2026-01-02 22:00               4 2026-01-02 22:00:00
     200 2026-01-01 22:00               4 2026-01-01 22:00:00
     229 2026-01-12 12:00               4 2026-01-12 12:00:00
     287 2026-01-14 14:00               4 2026-01-14 14:00:00
     314 2026-01-02 18:00               4 2026-01-02 18:00:00
     345 2026-01-23 09:00               4 2026-01-23 09:00:00

