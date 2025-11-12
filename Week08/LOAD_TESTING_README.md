# Load Testing và Stress Testing với Locust

## Cài đặt

### 1. Cài đặt Locust
```powershell
pip install locust
```

### 2. Hoặc cài đặt từ requirements
```powershell
pip install -r requirements.txt
```

## Cấu trúc File

- **locustfile.py** - File chính chứa các test scenarios
- **locust_commands.ps1** - PowerShell scripts cho các test scenarios
- **locust_commands.sh** - Bash scripts (Linux/Mac)

## Các Class Test Có Sẵn

### 1. WebsiteUser (Default)
Mô phỏng hành vi người dùng thực tế:
- Login → Create Product → List Products → Get Product → Update → Delete
- Wait time: 1-3 giây giữa các request
- Phù hợp cho: **Load Testing**

### 2. QuickLoadTest
Test tập trung vào đọc dữ liệu:
- 70% List Products
- 25% Get Product
- 5% Create Product
- Wait time: 0.5-2 giây
- Phù hợp cho: **Quick Testing, Smoke Testing**

### 3. StressTest
Test với tải cao và wait time ngắn:
- 50% List (rapid)
- 25% Get (rapid)
- 25% Create (rapid)
- Wait time: 0.1-0.5 giây
- Phù hợp cho: **Stress Testing, Performance Limits**

## Cách Chạy

### Mode 1: Interactive Web UI
```powershell
# Start Locust với Web UI
locust -f locustfile.py --host=http://localhost:8080

# Truy cập http://localhost:8089 để điều khiển test
```

### Mode 2: Headless (Automated)
```powershell
# Load Test - 50 users, 5 phút
locust -f locustfile.py --host=http://localhost:8080 `
  --users 50 `
  --spawn-rate 5 `
  --run-time 5m `
  --html load_test_report.html

# Stress Test - 200 users với StressTest class
locust -f locustfile.py --host=http://localhost:8080 `
  --users 200 `
  --spawn-rate 20 `
  --run-time 5m `
  --html stress_test_report.html `
  --user-class StressTest

# Quick Smoke Test
locust -f locustfile.py --host=http://localhost:8080 `
  --users 10 `
  --spawn-rate 2 `
  --run-time 1m `
  --html smoke_test_report.html `
  --user-class QuickLoadTest
```

### Mode 3: CSV Export
```powershell
# Export kết quả ra CSV
locust -f locustfile.py --host=http://localhost:8080 `
  --users 100 `
  --spawn-rate 10 `
  --run-time 5m `
  --headless `
  --csv test_results
```

## Các Kịch Bản Test

### 1. Load Test (Tải Bình Thường)
**Mục đích:** Kiểm tra hiệu suất với tải người dùng thực tế

```powershell
locust -f locustfile.py --host=http://localhost:8080 `
  --users 50 --spawn-rate 5 --run-time 5m `
  --html load_test_report.html
```

**Kỳ vọng:**
- Response time < 200ms cho 95% requests
- Error rate < 1%
- Throughput ổn định

### 2. Stress Test (Tải Cao)
**Mục đích:** Tìm giới hạn của hệ thống

```powershell
locust -f locustfile.py --host=http://localhost:8080 `
  --users 200 --spawn-rate 20 --run-time 5m `
  --html stress_test_report.html --user-class StressTest
```

**Kỳ vọng:**
- Xác định breaking point
- Monitor error rates
- Kiểm tra recovery

### 3. Spike Test (Tăng Đột Ngột)
**Mục đích:** Test khả năng xử lý tăng đột ngột traffic

```powershell
locust -f locustfile.py --host=http://localhost:8080 `
  --users 500 --spawn-rate 50 --run-time 3m `
  --html spike_test_report.html
```

**Kỳ vọng:**
- Hệ thống không crash
- Tự động scale (nếu có)
- Graceful degradation

### 4. Endurance Test (Bền Bỉ)
**Mục đích:** Test ổn định trong thời gian dài

```powershell
locust -f locustfile.py --host=http://localhost:8080 `
  --users 30 --spawn-rate 3 --run-time 30m `
  --html endurance_test_report.html
```

**Kỳ vọng:**
- Không có memory leak
- Performance ổn định
- Không có resource exhaustion

### 5. Smoke Test (Kiểm Tra Nhanh)
**Mục đích:** Validation nhanh sau deploy

```powershell
locust -f locustfile.py --host=http://localhost:8080 `
  --users 10 --spawn-rate 2 --run-time 1m `
  --html smoke_test_report.html --user-class QuickLoadTest
```

## Phân Tích Kết Quả

### Metrics Quan Trọng

1. **Response Time**
   - 50th percentile: Median response time
   - 95th percentile: 95% requests nhanh hơn giá trị này
   - 99th percentile: Edge cases

2. **Requests per Second (RPS)**
   - Throughput của hệ thống
   - Càng cao càng tốt

3. **Failure Rate**
   - Tỷ lệ request thất bại
   - Nên < 1% trong load test
   - Có thể cao hơn trong stress test

4. **Average Response Time**
   - Thời gian phản hồi trung bình
   - Tăng dần khi user tăng là bình thường

### Đọc HTML Report

Report HTML bao gồm:
- **Statistics**: Tổng hợp metrics theo endpoint
- **Charts**: Biểu đồ response time và RPS theo thời gian
- **Failures**: Chi tiết các request thất bại
- **Exceptions**: Các exception xảy ra

## Tips và Best Practices

1. **Chạy API Server trước:**
   ```powershell
   uvicorn openapi_server.main:app --host 0.0.0.0 --port 8080
   ```

2. **Start nhẹ, tăng dần:**
   - Bắt đầu với số user ít
   - Tăng dần để tìm breaking point

3. **Monitor Server:**
   - CPU usage
   - Memory usage
   - Database connections
   - Network I/O

4. **Realistic scenarios:**
   - Sử dụng WebsiteUser cho test giống người dùng thực
   - Adjust wait_time phù hợp với use case

5. **Clean up data:**
   - Xóa test data sau khi test xong
   - Hoặc dùng separate test database

## Distributed Load Testing

Cho test với số lượng user lớn hơn:

**Master node:**
```powershell
locust -f locustfile.py --master --expect-workers 2
```

**Worker nodes:**
```powershell
locust -f locustfile.py --worker --master-host=localhost
```

## Troubleshooting

### Error: "Too many open files"
Tăng file descriptor limit trên Linux/Mac:
```bash
ulimit -n 10000
```

### Error: Connection refused
- Kiểm tra API server đang chạy
- Kiểm tra port đúng
- Kiểm tra firewall

### Low RPS
- Tăng --users
- Giảm wait_time trong code
- Check server performance

## Ví Dụ Workflow Hoàn Chỉnh

```powershell
# 1. Start API Server
uvicorn openapi_server.main:app --host 0.0.0.0 --port 8080

# 2. Run Smoke Test
locust -f locustfile.py --host=http://localhost:8080 `
  --users 10 --spawn-rate 2 --run-time 1m `
  --headless --html smoke_test_report.html

# 3. Run Load Test
locust -f locustfile.py --host=http://localhost:8080 `
  --users 50 --spawn-rate 5 --run-time 5m `
  --headless --html load_test_report.html

# 4. Run Stress Test
locust -f locustfile.py --host=http://localhost:8080 `
  --users 200 --spawn-rate 20 --run-time 5m `
  --headless --html stress_test_report.html --user-class StressTest

# 5. Analyze reports
# Open HTML reports in browser
```

## Tài Liệu Tham Khảo

- [Locust Documentation](https://docs.locust.io/)
- [Writing Locust Tests](https://docs.locust.io/en/stable/writing-a-locustfile.html)
- [Distributed Testing](https://docs.locust.io/en/stable/running-distributed.html)
