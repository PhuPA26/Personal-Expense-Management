import csv
import random
from datetime import datetime, timedelta

# 1. Định nghĩa danh sách danh mục theo yêu cầu của bạn
# Cấu trúc: (id, name, type)
categories = [
    ("ăn uống", "Ăn uống", "expense"),
    ("đi lại", "Đi lại", "expense"),
    ("học tập", "Học tập", "expense"),
    ("sinh hoạt", "Sinh hoạt", "expense"),
    ("giải trí", "Giải trí", "expense"),
    ("lương", "Lương", "income"),
    ("thưởng", "Thưởng", "income"),
    ("cho vay", "Cho vay", "expense"),
    ("thu nợ", "Thu nợ", "income"),
    ("đi vay", "Đi vay", "income"),
    ("trả nợ", "Trả nợ", "expense")
]

# Tách riêng danh mục thu và chi để sinh số tiền hợp lý
income_cats = [c for c in categories if c[2] == "income"]
expense_cats = [c for c in categories if c[2] == "expense"]

# 2. Cấu hình sinh dữ liệu
TOTAL_TRANSACTIONS = 10000
FILE_NAME = "transactions_stress_test.csv"

# Thiết lập khoảng thời gian ngẫu nhiên (từ 01/01/2025 đến 31/05/2026)
start_date = datetime(2025, 1, 1)
end_date = datetime(2026, 5, 31)
delta_days = (end_date - start_date).days

print(f"🔄 Đang tạo {TOTAL_TRANSACTIONS} giao dịch mẫu...")

# 3. Tiến hành sinh dữ liệu và ghi vào file CSV
with open(FILE_NAME, mode="w", encoding="utf-8", newline="") as file:
    # Định nghĩa các cột tương ứng với cấu trúc file dữ liệu của bạn
    # Ví dụ phổ biến: Mã_GD, Ngày, Danh_Mục_ID, Tên_Danh_Mục, Loại, Số_Tiền, Ghi_Chú
    writer = csv.writer(file, delimiter="|")
    
    # Ghi tiêu đề nếu hệ thống của bạn yêu cầu (nếu không cần thì có thể comment dòng này)
    writer.writerow(["Transaction_ID", "Date", "Category_ID", "Category_Name", "Type", "Amount", "Note"])
    
    for i in range(1, TOTAL_TRANSACTIONS + 1):
        # Tạo mã giao dịch tự tăng dạng TX00001
        tx_id = f"TX{i:05d}"
        
        # Sinh ngày ngẫu nhiên
        random_days = random.randint(0, delta_days)
        tx_date = (start_date + timedelta(days=random_days)).strftime("%d/%m/%Y")
        
        # Tỷ lệ: 20% là khoản Thu (income) để đảm bảo số dư dương, 80% là Khoản Chi (expense)
        if random.random() < 0.20:
            cat = random.choice(income_cats)
            # Tiền thu (Lương/Thưởng...) thường lớn
            amount = float(random.randint(500, 2000) * 10000) 
        else:
            cat = random.choice(expense_cats)
            # Tiền chi tiêu hàng ngày nhỏ hơn, dao động từ 10k đến 500k
            if cat[0] in ["cho vay", "trả nợ"]:
                amount = float(random.randint(100, 1000) * 10000) # Khoản vay/trả thường lớn hơn
            else:
                amount = float(random.randint(1, 50) * 10000)
        
        note = f"Giao dich stress test so {i}"
        
        # Ghi một dòng giao dịch xuống file theo đúng định dạng dấu gạch đứng '|' giống như file của bạn
        writer.writerow([tx_id, tx_date, cat[0], cat[1], cat[2], amount, note])

print(f"✅ Đã tạo thành công file '{FILE_NAME}' phục vụ chạy Stress Test!")