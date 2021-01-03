-- bill adjustment
SELECT cls_amt-(opn_amt-(((end_eb-start_eb)*eb_price)+((end_dg-start_dg)*dg_price)) +
	(select sum(recharge) from users_recharge as rc where 
		EXTRACT(MONTH FROM rc.dt) = 4 and EXTRACT(YEAR FROM rc.dt) = 2020 and flat_id=bill.flat_id
	) - (select sum(mcharge)+sum(famt) from users_maintance as mc where 
		EXTRACT(MONTH FROM mc.dt) = 4 and EXTRACT(YEAR FROM mc.dt) = 2020 and flat_id=bill.flat_id
	))
	AS Adjustment, cls_amt, flat_id	, flat.tower, flat.flat
  FROM public.users_monthlybill as bill inner join public.users_flats as flat 
  on bill.flat_id = flat.id
  where bill.month=4 and bill.year=2020 order by Adjustment

-- end bill adjustment


-- Updated on bill adjustment

SELECT * FROM
(SELECT cls_amt-(opn_amt-(((end_eb-start_eb)*eb_price)+((end_dg-start_dg)*dg_price)) +
	(select sum(recharge) from users_recharge as rc where 
		EXTRACT(MONTH FROM rc.dt) = 4 and EXTRACT(YEAR FROM rc.dt) = 2020 and flat_id=bill.flat_id
	) - (select sum(mcharge)+sum(famt) from users_maintance as mc where 
		EXTRACT(MONTH FROM mc.dt) = 4 and EXTRACT(YEAR FROM mc.dt) = 2020 and flat_id=bill.flat_id
	))
	AS Adjustment, cls_amt, flat_id	, flat.tower, flat.flat
  FROM public.users_monthlybill as bill inner join public.users_flats as flat 
  on bill.flat_id = flat.id
  where bill.month=1 and bill.year=2020 order by Adjustment
) as innerTable WHERE Adjustment > 1;

-- End bill adjustment

-- after debit

SELECT * FROM
(SELECT (opn_amt-(((end_eb-start_eb)*eb_price)+((end_dg-start_dg)*dg_price)) +
	(select sum(recharge) from users_recharge as rc where 
		EXTRACT(MONTH FROM rc.dt) = 10 and EXTRACT(YEAR FROM rc.dt) = 2020 and flat_id=bill.flat_id
	) - (select sum(mcharge)+sum(famt) from users_maintance as mc where 
		EXTRACT(MONTH FROM mc.dt) = 10 and EXTRACT(YEAR FROM mc.dt) = 2020 and flat_id=bill.flat_id
	) - (select sum(debit_amt) from users_debit as ud where 
		EXTRACT(MONTH FROM ud.dt) = 10 and EXTRACT(YEAR FROM ud.dt) = 2020 and flat_id=bill.flat_id
	))-cls_amt
	AS Adjustment, cls_amt, flat_id	, flat.tower, flat.flat
  FROM public.users_monthlybill as bill inner join public.users_flats as flat 
  on bill.flat_id = flat.id
  where bill.month=10 and bill.year=2020 order by flat.tower, flat.flat
) as innerTable WHERE Adjustment not between -1 and 1;

-- end after debit


SELECT * FROM
(SELECT (opn_amt-(((end_eb-start_eb)*eb_price)+((end_dg-start_dg)*dg_price)) +
	(select sum(recharge) from users_recharge as rc where 
		EXTRACT(MONTH FROM rc.dt) = 10 and EXTRACT(YEAR FROM rc.dt) = 2020 and flat_id=bill.flat_id
	) - (select sum(mcharge)+sum(famt) from users_maintance as mc where 
		EXTRACT(MONTH FROM mc.dt) = 10 and EXTRACT(YEAR FROM mc.dt) = 2020 and flat_id=bill.flat_id
	) - (select sum(debit_amt) from users_debit as ud where 
		EXTRACT(MONTH FROM ud.dt) = 10 and EXTRACT(YEAR FROM ud.dt) = 2020 and flat_id=bill.flat_id
	))-cls_amt
	AS Adjustment, cls_amt, flat_id	, flat.tower, flat.flat
  FROM public.users_monthlybill as bill inner join public.users_flats as flat 
  on bill.flat_id = flat.id
  where bill.month=10 and bill.year=2020 order by flat.tower, flat.flat
) as innerTable WHERE Adjustment IS NOT NULL;

-- panthouse
SELECT tower, flat
FROM public.users_flats as flt
where tower=flt.tower and flat > (SELECT(max(flat)-max(flat)%100) As remain
  FROM public.users_flats where tower=flt.tower) and tower!=17 order by tower, flat;
-- end panthouse

SELECT 
(select tower from users_flats where id=reading.flat_id), (select flat from users_flats where id=reading.flat_id), 
ROUND(min(eb), 2) as START_EB, ROUND(max(eb), 2) as END_EB, ROUND(min(dg), 2) as START_DG,ROUND(max(dg), 2) as END_DG,
(select ROUND((sum(mcharge)/2.79)*1.79, 2) from users_maintance where flat_id=reading.flat_id and  dt between '2020-07-13' and '2020-08-06') as Maintance,
(select ROUND(sum(mcharge)/2.79, 2) from users_maintance where flat_id=reading.flat_id and  dt between '2020-07-13' and '2020-08-06') as Paint,
(select ROUND(sum(famt), 2) from users_maintance where flat_id=reading.flat_id and  dt between '2020-07-13' and '2020-08-06') as Fixed_Charge
	FROM public.users_reading as reading where dt between '2020-07-13' and '2020-08-06' group by flat_id order by tower,flat;