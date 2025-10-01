import pyodbc
from flask import Flask, render_template, request, redirect
from azure.storage.blob import BlobServiceClient

app = Flask(__name__)


AZURE_SQL_CONNECTION = (
    "Driver={ODBC Driver 18 for SQL Server};"
    "Server=tcp:kietsqlserver.database.windows.net,1433;"
    "Database=UserDB;"
    "Uid=sqladmin;"
    "Pwd=Tranhoangkiet@123;"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
    "Connection Timeout=30;"
)

AZURE_STORAGE_CONNECTION = "DefaultEndpointsProtocol=https;AccountName=kiettranstorage;AccountKey=Vn8iMlZUi7bpHbJf2S7doC2xOz3XNjb056P9XJszY4Oq5zYgwRAh52aQzpWP+y0To/Cqo/WWFyhD+ASt+g5h9w==;EndpointSuffix=core.windows.net"
AZURE_STORAGE_CONTAINER = "userbackup"


def get_sql_connection():
    conn = pyodbc.connect(AZURE_SQL_CONNECTION)
    return conn


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone"]

        # Thêm vào Azure SQL
        conn = get_sql_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO dbo.[User] (Name, Phone) VALUES (?, ?)", (name, phone))
        conn.commit()
        conn.close()

        # Lưu vào Azure Storage
        blob_service = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION)
        container_client = blob_service.get_container_client(AZURE_STORAGE_CONTAINER)
        blob_name = f"user_{name}.txt"
        blob_content = f"Name: {name}, Phone: {phone}"
        container_client.upload_blob(blob_name, blob_content, overwrite=True)

        return redirect("/")

    # Đọc dữ liệu từ SQL
    conn = get_sql_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT Id, Name, Phone FROM dbo.[User]")
    rows = cursor.fetchall()
    conn.close()

    return render_template("index.html", users=rows)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
