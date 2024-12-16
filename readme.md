
# 🚀 **Backend Project Setup Guide**

Follow these steps to get the TravelPlanner backend up and running smoothly!

---

**Step 1: Navigate to the Root Directory**
Fire up your terminal and step into the project's home base:

```bash
cd /travelplanner-backend
```

## **Step 2: Install Dependencies**
Get your environment ready by installing all the required packages. Just run:

```bash
pip3 install -r ./requirements.txt
pip install 'uvicorn[standard]'
```

✅ **Pro Tip**: Make sure you're in a virtual environment to keep things clean and organized!

---

## **Step 3: Start the Backend Server**
With everything set, let's bring your project to life. Start the development server by running:

```bash
python -m uvicorn main:app --reload
```

🌟 **Success!** Your backend is now live and reloading automatically for every code change. Open your browser or tool of choice, and you're good to go.
