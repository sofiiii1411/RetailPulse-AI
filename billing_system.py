import firebase_admin
from firebase_admin import credentials, db
import qrcode
from datetime import datetime
import openpyxl
import os
import webbrowser
import uuid

# ---------------- FIREBASE CONNECTION ----------------

cred = credentials.Certificate("retailpulseai-e2a4a-firebase-adminsdk-fbsvc-a29aa4fe45.json")

firebase_admin.initialize_app(cred, {
    "databaseURL": "https://retailpulseai-e2a4a-default-rtdb.firebaseio.com/"
})

ref = db.reference("billing_records")

# ---------------- AUTO GENERATED IDS ----------------

shop_id = "SHOP001"
bill_id = "BILL-" + str(uuid.uuid4())[:6]

print("\nSMART BILLING SYSTEM")

# ---------------- PHONE NUMBER VALIDATION ----------------

while True:

    phone = input("Enter Customer Phone Number: ")

    if phone.isdigit() and len(phone) == 10:
        break
    else:
        print("❌ Invalid number! Enter 10 digit phone number.")

# ---------------- AUTO CUSTOMER ID ----------------

customer_id = "CUST-" + phone[-4:]

# ---------------- CHECK CUSTOMER HISTORY ----------------

records = ref.get()

print("\nCUSTOMER HISTORY\n")

found = False

if records:

    for key, value in records.items():

        if value.get("phone") == phone:

            found = True

            print("BillID:", value["billID"])
            print("Date:", value["date"], value["time"])
            print("Total: ₹", value["totalAmount"])
            print("Payment:", value["paymentType"])
            print("Status:", value["status"])
            print("-------------------")

if not found:
    print("No previous purchases.")

# ---------------- PRODUCT ENTRY ----------------

print("\nEnter products (type . to finish)\n")

items = []
total = 0
total_quantity = 0

while True:

    product = input("Enter product name: ").upper()

    if product == ".":
        break

    price = float(input("Enter price: "))
    qty = int(input("Enter quantity: "))

    amount = price * qty

    total += amount
    total_quantity += qty

    items.append((product, qty, price, amount))

# ---------------- BILL DISPLAY ----------------

print("\n----------- BILL -----------")

print("{:<15} {:<8} {:<10} {:<10}".format("PRODUCT","QTY","PRICE","TOTAL"))
print("--------------------------------")

for item in items:
    print("{:<15} {:<8} {:<10} {:<10}".format(item[0], item[1], item[2], item[3]))

print("--------------------------------")
print("TOTAL AMOUNT = ₹", total)

# ---------------- DATE TIME ----------------

now = datetime.now()

date = now.strftime("%d-%m-%Y")
time = now.strftime("%H:%M:%S")

# ---------------- PAYMENT TYPE ----------------

while True:

    payment_type = input("Payment Type (UPI/CASH/CARD): ").upper()

    if payment_type in ["UPI","CASH","CARD"]:
        break
    else:
        print("Enter valid payment type.")

# ---------------- UPI QR CODE ----------------

status = "PENDING"

if payment_type == "UPI":

    upi_id = "sofianu723@okicici"

    note = ",".join([f"{i[0]}x{i[1]}" for i in items])

    upi_link = f"upi://pay?pa={upi_id}&pn=RetailPulseStore&am={total}&cu=INR&tn={note}"

    qr = qrcode.make(upi_link)
    qr_file = "payment_qr.png"
    qr.save(qr_file)

    print("\nUPI QR Code Generated")

    try:
        os.startfile(qr_file)
    except:
        webbrowser.open(qr_file)

    status = input("Payment done? (PAID/PENDING): ").upper()

else:

    status = "PAID"

# ---------------- EXCEL SAVE ----------------

try:

    wb = openpyxl.load_workbook("sales.xlsx")
    sheet = wb.active

except:

    wb = openpyxl.Workbook()
    sheet = wb.active

    sheet.append([
        "ShopID","BillID","CustomerID","Phone",
        "Date","Time","Product","Qty",
        "Price","Total","PaymentType","Status"
    ])

for item in items:

    sheet.append([
        shop_id,
        bill_id,
        customer_id,
        phone,
        date,
        time,
        item[0],
        item[1],
        item[2],
        item[3],
        payment_type,
        status
    ])

wb.save("sales.xlsx")

# ---------------- FIREBASE SAVE ----------------

bill_data = {

    "shopID": shop_id,
    "billID": bill_id,
    "customerID": customer_id,
    "phone": phone,
    "paymentType": payment_type,
    "date": date,
    "time": time,
    "totalQuantity": total_quantity,
    "totalAmount": total,
    "status": status,
    "items": []

}

for item in items:

    bill_data["items"].append({

        "productName": item[0],
        "quantity": item[1],
        "price": item[2],
        "total": item[3]

    })

ref.push(bill_data)

# ---------------- SUCCESS ----------------

print("\nBill saved successfully")
print("ShopID:", shop_id)
print("BillID:", bill_id)
print("CustomerID:", customer_id)
print("Saved to Firebase")