from dotenv import load_dotenv
import os
import razorpay

rzclient = razorpay.Client(auth=(os.getenv("RAZORPAY_API_KEY"), os.getenv("RAZORPAY_API_SECRET")))
rzclient.set_app_details({"title" : "<YOUR_APP_TITLE>", "version" : "<YOUR_APP_VERSION>"})

print(rzclient)

load_dotenv()

print(os.getenv("RAZORPAY_API_KEY"))
print(os.getenv("RAZORPAY_API_SECRET"))
