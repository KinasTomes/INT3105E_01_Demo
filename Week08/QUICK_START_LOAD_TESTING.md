# Quick Start Guide - Locust Load Testing

## Bước 1: Đảm bảo API Server đang chạy

Mở terminal và chạy:
```powershell
uvicorn openapi_server.main:app --host 0.0.0.0 --port 8080
```

## Bước 2: Chạy Load Test

### Option 1: Sử dụng Script Tự Động (Khuyến nghị)
```powershell
python run_load_tests.py
```

Chọn test scenario từ menu:
- **1** - Smoke Test (nhanh, 1 phút)
- **2** - Load Test (5 phút)
- **3** - Stress Test (200 users)
- **7** - Chạy tất cả tests

### Option 2: Chạy Trực Tiếp với Locust

#### Smoke Test (Quick Check)
```powershell
locust -f locustfile_quick.py --host=http://localhost:8080 `
  --users 10 --spawn-rate 2 --run-time 1m `
  --headless --html smoke_test_report.html
```

#### Load Test (Standard)
```powershell
locust -f locustfile.py --host=http://localhost:8080 `
  --users 50 --spawn-rate 5 --run-time 5m `
  --headless --html load_test_report.html
```

#### Stress Test (Heavy Load)
```powershell
locust -f locustfile_stress.py --host=http://localhost:8080 `
  --users 200 --spawn-rate 20 --run-time 5m `
  --headless --html stress_test_report.html
```

### Option 3: Interactive Web UI
```powershell
locust -f locustfile.py --host=http://localhost:8080
```

Sau đó mở trình duyệt: http://localhost:8089

## Bước 3: Xem Kết Quả

Sau khi test hoàn tất, mở file HTML report trong thư mục project:
- `smoke_test_report.html`
- `load_test_report.html`
- `stress_test_report.html`

## Các Metrics Quan Trọng

- **Request Count**: Tổng số requests
- **Failure Rate**: Tỷ lệ thất bại (nên < 1%)
- **Average Response Time**: Thời gian phản hồi trung bình
- **RPS**: Requests per second (throughput)
- **95th percentile**: 95% requests nhanh hơn giá trị này

## Troubleshooting

### Lỗi: Connection refused
- Đảm bảo API server đang chạy
- Kiểm tra port 8080 chưa bị dùng

### Lỗi: Locust not found
```powershell
pip install locust
```

### Muốn test với nhiều users hơn
Tăng số `--users` và `--spawn-rate`:
```powershell
locust -f locustfile.py --host=http://localhost:8080 `
  --users 500 --spawn-rate 50 --run-time 5m `
  --headless --html high_load_test.html
```

## Ví Dụ Output

```
[2025-11-12 18:00:00,000] INFO/locust.main: Starting Locust 2.42.2
[2025-11-12 18:00:00,100] INFO/locust.main: Run time limit set to 300 seconds
[2025-11-12 18:00:00,200] INFO/locust.runners: Spawning 50 users at the rate 5 users/s...
[2025-11-12 18:05:00,000] INFO/locust.main: Time limit reached. Stopping Locust.

Name                          # reqs      # fails  |     Avg     Min     Max  Median  |   req/s  failures/s
----------------------------------------------------------------------------------------------------------
POST /auth/login                  50     0(0.00%)  |     120      98     234     110  |    0.17    0.00
GET /products                    500     0(0.00%)  |      89      45     345      85  |    1.67    0.00
POST /products                   100     1(1.00%)  |     156      89     567     145  |    0.33    0.00
----------------------------------------------------------------------------------------------------------
Aggregated                       650     1(0.15%)  |      98      45     567      90  |    2.17    0.00

Response time percentiles (approximated):
Type     Name                          50%    66%    75%    80%    90%    95%    98%    99%  99.9% 99.99%   100%
--------|-----------------------------|--------|------|------|------|------|------|------|------|------|------|------
POST     /auth/login                   110    125    145    156    189    213    234    234    234    234    234
GET      /products                      85     98    110    123    178    234    298    345    345    345    345
POST     /products                     145    167    189    201    278    345    456    567    567    567    567
--------|-----------------------------|--------|------|------|------|------|------|------|------|------|------|------
         Aggregated                     90    110    134    156    212    267    345    456    567    567    567
```

## Đọc Thêm

Chi tiết đầy đủ trong `LOAD_TESTING_README.md`
