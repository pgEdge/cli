START TRANSACTION ISOLATION LEVEL REPEATABLE READ;

SELECT CASE count(*) WHEN 0 THEN 'OK   ' ELSE 'ERROR' END AS "check",
    count(*) AS "count", 'bbalance <> history.sum(delta)' AS "description"
    FROM (
        SELECT B.bid, B.bbalance, sum(H.delta)
        FROM pgbench_branches B
        LEFT JOIN pgbench_history H ON B.bid = H.bid
        GROUP BY B.bid
        HAVING B.bbalance <> sum(H.delta)
    ) AS X;

SELECT CASE count(*) WHEN 0 THEN 'OK   ' ELSE 'ERROR' END AS "check",
    count(*) AS "count", 'tbalance <> history.sum(delta)' AS "description"
    FROM (
        SELECT T.tid, T.tbalance, sum(H.delta)
        FROM pgbench_tellers T
        LEFT JOIN pgbench_history H ON T.tid = H.tid
        GROUP BY T.tid
        HAVING T.tbalance <> sum(H.delta)
    ) AS X;

SELECT CASE count(*) WHEN 0 THEN 'OK   ' ELSE 'ERROR' END AS "check",
    count(*) AS "count", 'abalance <> history.sum(delta)' AS "description"
    FROM (
        SELECT A.aid, A.abalance, sum(H.delta)
        FROM pgbench_accounts A
        LEFT JOIN pgbench_history H ON A.aid = H.aid
        GROUP BY A.aid
        HAVING A.abalance <> sum(H.delta)
    ) AS X;

ROLLBACK;

