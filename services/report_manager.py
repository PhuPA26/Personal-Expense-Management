from data import index_services

class ReportManager:
    def __init__(self, month_index):
        self._month_index = month_index

    def generate_monthly_report(self, year, month):
        # 1. TRUY XUẤT DỮ LIỆU THÁNG
        month_data = self._month_index.get(year, month)
        
        print("\n" + "="*55)
        print(f"        BÁO CÁO TÀI CHÍNH THÁNG {month:02d}/{year}        ")
        print("="*55)

        if month_data is None:
            print(f" ❌ Không tìm thấy dữ liệu giao dịch nào cho tháng {month:02d}/{year}.")
            print("="*55)
            return
        
        # 2. TỔNG HỢP SỐ LIỆU THU / CHI
        total_income = 0
        total_expense = 0
        expense_list = []

        # Quét qua toàn bộ các CategoryState trong tháng thông qua bảng băm
        for state_id in month_data.category_states.keys():
            state = month_data.category_states.get(state_id)
            
            # Phân loại dựa trên thuộc tính type của danh mục gốc (category.type)
            # Đồng bộ xử lý chuỗi chữ thường theo model.py và CategoryManager.py
            cat_type = state.category.type.lower()
            
            if cat_type == "income":
                total_income += state.total_income
            elif cat_type == "expense":
                total_expense += state.total_expense
                if state.total_expense > 0:
                    expense_list.append(state)

        net_savings = total_income - total_expense
        
        print(f" 💰 Tổng thu nhập    : {total_income:,.0f} đ")
        print(f" 💸 Tổng chi tiêu    : {total_expense:,.0f} đ")
        print(f" ⚖️ Thặng dư tích lũy: {net_savings:,.0f} đ " + ("📈" if net_savings >= 0 else "📉"))
        print("-" * 55)

        # 3. ĐỒ HỌA CHỮ: TỶ LỆ CHI TIÊU GIỮA CÁC NHÓM
        print(" 📊 BIỂU ĐỒ TỶ LỆ CHI TIÊU GIỮA CÁC DANH MỤC:")
        if total_expense == 0:
            print("   (Chưa có dữ liệu chi tiêu để hiển thị biểu đồ)")
        else:
            for state in expense_list:
                percentage = (state.total_expense / total_expense) * 100
                
                # Tính độ dài thanh đồ thị (Tối đa 20 ký tự ứng với 100%)
                bar_length = int(percentage / 5)
                bar_visual = "■" * bar_length if bar_length > 0 else "·"
                
                print(f"   • {state.category.name:<15} | {bar_visual:<20} | {percentage:6.1f}% ({state.total_expense:,.0f} đ)")
        print("-" * 55)


        # 4. TỔNG HỢP CÁC MỤC VƯỢT BUDGET (NGÂN SÁCH)
        print("DANH SÁCH DANH MỤC VƯỢT NGÂN SÁCH (BUDGET):")
        over_budget_count = 0
        
        for state in expense_list:
            # Lấy chính xác hạn mức lịch sử lưu trong State của tháng đó
            limit = state.limit
            
            if state.total_expense > limit:
                over_budget_count += 1
                amount_over = state.total_expense - limit
                percent_over = (amount_over / limit) * 100 if limit > 0 else 100
                
                print(f"   ❌ [{state.category.name}] ĐÃ VƯỢT HẠN MỨC!")
                print(f"      - Ngân sách đặt ra : {limit:,.0f} đ")
                print(f"      - Thực tế đã chi   : {state.total_expense:,.0f} đ")
                print(f"      - Số tiền vượt quá : +{amount_over:,.0f} đ ({percent_over:.1f}%)")
                print()
                
        if over_budget_count == 0:
            print("Tuyệt vời! không có danh mục nào chi tiêu vượt hạn mức.")
            
            
        print("="*55 + "\n")

    def generate_daily_report(self, year, month, day):
        month_data = self._month_index.get(year, month)
        
        print("\n" + "="*55)
        print(f"        BÁO CÁO TÀI CHÍNH NGÀY {day:02d}/{month:02d}/{year}        ")
        print("="*55)

        if month_data is None:
            print(f" ❌ Không tìm thấy dữ liệu giao dịch nào cho ngày {day:02d}/{month:02d}/{year}.")
            print("="*55)
            return

        import datetime
        target_date = datetime.date(year, month, day)
        
        transaction_index = index_services.TransactionIndex(month_data)
        first, last = transaction_index.find_by_date(target_date)
        
        if first < 0:
            print(f" ❌ Không có giao dịch nào trong ngày {day:02d}/{month:02d}/{year}.")
            print("="*55)
            return
            
        transactions = transaction_index._transactions[first:last+1]
        
        total_income = 0
        total_expense = 0
        
        print(" DANH SÁCH GIAO DỊCH:")
        for tx in transactions:
            cat = month_data.category_states.get(tx.category_id).category
            if tx.transaction_type.lower() == "income":
                total_income += tx.amount
                print(f"   [+] {tx.amount:>10,.0f} đ | {cat.name:<15} | {tx.note}")
            else:
                total_expense += tx.amount
                print(f"   [-] {tx.amount:>10,.0f} đ | {cat.name:<15} | {tx.note}")
                
        net_savings = total_income - total_expense
        print("-" * 55)
        print(f" 💰 Tổng thu    : {total_income:,.0f} đ")
        print(f" 💸 Tổng chi    : {total_expense:,.0f} đ")
        print(f" ⚖️ Thặng dư    : {net_savings:,.0f} đ " + ("📈" if net_savings >= 0 else "📉"))
        print("="*55 + "\n")

    def generate_yearly_report(self, year):
        print("\n" + "="*55)
        print(f"        BÁO CÁO TÀI CHÍNH NĂM {year}        ")
        print("="*55)
        
        total_income = 0
        total_expense = 0
        category_totals = {}
        
        found_data = False
        
        for month in range(1, 13):
            month_data = self._month_index.get(year, month)
            if month_data is None:
                continue
                
            found_data = True
            for state_id in month_data.category_states.keys():
                state = month_data.category_states.get(state_id)
                cat_type = state.category.type.lower()
                cat_name = state.category.name
                
                if cat_type == "income":
                    total_income += state.total_income
                elif cat_type == "expense":
                    total_expense += state.total_expense
                    category_totals[cat_name] = category_totals.get(cat_name, 0) + state.total_expense
                    
        if not found_data:
            print(f" ❌ Không có dữ liệu giao dịch nào trong năm {year}.")
            print("="*55)
            return
            
        net_savings = total_income - total_expense
        
        print(f" 💰 Tổng thu nhập năm    : {total_income:,.0f} đ")
        print(f" 💸 Tổng chi tiêu năm    : {total_expense:,.0f} đ")
        print(f" ⚖️ Thặng dư tích lũy năm: {net_savings:,.0f} đ " + ("📈" if net_savings >= 0 else "📉"))
        print("-" * 55)
        
        print(" 📊 BIỂU ĐỒ TỶ LỆ CHI TIÊU CẢ NĂM GIỮA CÁC DANH MỤC:")
        if total_expense == 0:
            print("   (Chưa có dữ liệu chi tiêu để hiển thị biểu đồ)")
        else:
            for cat_name, amt in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
                percentage = (amt / total_expense) * 100
                bar_length = int(percentage / 5)
                bar_visual = "■" * bar_length if bar_length > 0 else "·"
                print(f"   • {cat_name:<15} | {bar_visual:<20} | {percentage:6.1f}% ({amt:,.0f} đ)")
                
        print("="*55 + "\n")

    def generate_k_months_report(self, k_months):
        import datetime
        now = datetime.datetime.now()
        current_year = now.year
        current_month = now.month
        
        print("\n" + "="*55)
        print(f"  -- TỔNG QUAN CHI TIÊU {k_months} THÁNG GẦN NHẤT --")
        print("="*55)
        
        total_k_months_expense = 0
        months_with_data = 0
        
        for i in range(k_months):
            calc_month = current_month - i
            calc_year = current_year
            
            while calc_month <= 0:
                calc_month += 12
                calc_year -= 1
                
            month_data = self._month_index.get(calc_year, calc_month)
            if month_data is None:
                print(f" * Tháng {calc_month:02d}/{calc_year}: Tổng thu 0 đ, Tổng chi 0 đ, Thặng dư 0 đ")
                continue
                
            months_with_data += 1
            monthly_income = 0
            monthly_expense = 0
            
            for state_id in month_data.category_states.keys():
                state = month_data.category_states.get(state_id)
                cat_type = state.category.type.lower()
                if cat_type == "income":
                    monthly_income += state.total_income
                elif cat_type == "expense":
                    monthly_expense += state.total_expense
                    
            total_k_months_expense += monthly_expense
            surplus = monthly_income - monthly_expense
            
            warning = " ⚠️" if surplus < 0 else ""
            print(f" * Tháng {calc_month:02d}/{calc_year}: Tổng thu {monthly_income:,.0f} đ, Tổng chi {monthly_expense:,.0f} đ, Thặng dư {surplus:,.0f} đ{warning}")
            
        print("-" * 55)
        if months_with_data > 0:
            average_expense = total_k_months_expense / k_months
            print(f" => TRUNG BÌNH CHI TIÊU TOÀN GIAI ĐOẠN: {average_expense:,.0f} đ / tháng.")
        else:
            print(" => TRUNG BÌNH CHI TIÊU TOÀN GIAI ĐOẠN: 0 đ / tháng.")
        print("="*55 + "\n")

    def get_k_months_transactions(self, k_months):
        import datetime
        now = datetime.datetime.now()
        current_year = now.year
        current_month = now.month
        
        all_transactions = []
        
        for i in range(k_months):
            calc_month = current_month - i
            calc_year = current_year
            
            while calc_month <= 0:
                calc_month += 12
                calc_year -= 1
                
            month_data = self._month_index.get(calc_year, calc_month)
            if month_data is None:
                continue
                
            all_transactions.extend(month_data.transactions)
            
        all_transactions.sort(key=lambda tx: tx.date, reverse=True)
        return all_transactions
