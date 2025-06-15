import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import json
import random
import string
import openpyxl
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from utils.excel_handler import ExcelHandler
from utils.file_handler import FileHandler
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Initialize handlers
excel_handler = ExcelHandler(app.config['EXCEL_FILE'])
file_handler = FileHandler(app.config['UPLOAD_FOLDER'])

@app.route('/upload_product_image/<product_name>', methods=['GET', 'POST'])
def upload_product_image(product_name):
    if request.method == 'POST':
        result = file_handler.handle_image_upload(request.files.get('file'), product_name)
        if result['success']:
            excel_handler.update_product_image(product_name, result['filepath'])
            flash('封面图片上传成功')
            return redirect(url_for('product_record', product_name=product_name))
        else:
            flash(result['message'])
            return redirect(request.url)
            
    return render_template('upload_product_image.html', product_name=product_name)

@app.route('/')
def home():
    categories = [
        {'name': 'CPU', 'image': 'static/uploads/cpu_image.jpg'},
        {'name': '主板', 'image': 'static/uploads/mb.jpg'},
        {'name': '内存', 'image': 'static/uploads/ram.jpg'},
        {'name': '显卡', 'image': 'static/uploads/gpu.jpg'},
        {'name': 'SSD', 'image': 'static/uploads/ssd.jpg'},
        {'name': '电源', 'image': 'static/uploads/psu.jpeg'},
        {'name': '机箱', 'image': 'static/uploads/case.jpg'},
        {'name': '风扇', 'image': 'static/uploads/fan.jpg'},
        {'name': '其他', 'image': 'static/uploads/others.jpg'},
        {'name': 'Laptop', 'image': 'static/uploads/laptop.jpg'},
    ]
    return render_template('home.html', categories=categories)

@app.route('/shipment_confirmation', methods=['GET', 'POST'])
def shipment_confirmation():
    if request.method == 'POST':
        try:
            data = request.get_json()
            if not data:
                return jsonify({"status": "fail", "message": "Invalid JSON data"}), 400

            # Generate order ID
            order_id = f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}"
            
            shipment_data = {
                'sender': data.get('sender', 'Nero'),
                'recipient': data.get('recipient', 'cataclysm'),
                'operation_time': data.get('operationTime', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                'products': data.get('products', []),
                'order_id': order_id
            }

            return render_template('shipment_confirmation.html', 
                                   shipment_data=shipment_data,
                                   current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        except Exception as e:
            return jsonify({"status": "fail", "message": str(e)}), 500
    
    return redirect(url_for('shipment_overview'))

@app.route('/shipment_overview')
def shipment_overview():
    try:
        products_by_category = excel_handler.get_products_by_category()
        return render_template('shipment_overview.html', products_by_category=products_by_category)
    except Exception as e:
        flash(f'Error loading inventory: {str(e)}')
        return redirect(url_for('home'))

@app.route('/process_shipment', methods=['POST'])
def process_shipment():
    try:
        data = request.get_json()
        result = excel_handler.process_shipment(
            sender=data.get('sender'),
            recipient=data.get('recipient'),
            operation_time=data.get('operationTime'),
            products=data.get('products', [])
        )
        
        if result['success']:
            return jsonify({"status": "success"}), 200
        else:
            return jsonify({"status": "fail", "message": result['message']}), 400

    except Exception as e:
        return jsonify({"status": "fail", "message": str(e)}), 500

@app.route('/category/<category_name>')
def show_category(category_name):
    try:
        products = excel_handler.get_products_by_category(category_name)
        return render_template('category.html', category_name=category_name, products=products)
    except Exception as e:
        flash(f'Error loading category: {str(e)}')
        return redirect(url_for('home'))

@app.route('/product/<product_name>')
def product_record(product_name):
    try:
        records = excel_handler.get_product_records(product_name)
        return render_template('product_record.html', product_name=product_name, records=records)
    except Exception as e:
        flash(f'Error loading product records: {str(e)}')
        return redirect(url_for('home'))

@app.route('/add_stock', methods=['POST'])
def add_stock():
    try:
        product_name = request.form['product_name']
        quantity = int(request.form['quantity'])
        recipient = request.form['recipient']

        result = excel_handler.update_stock(product_name, quantity, recipient)
        
        if result['success']:
            return redirect(url_for('product_record', product_name=product_name))
        else:
            return result['message'], 400

    except Exception as e:
        return f"操作失败：{str(e)}", 500

@app.route('/api/inventory/summary')
def inventory_summary():
    """API endpoint for inventory summary"""
    try:
        summary = excel_handler.get_inventory_summary()
        return jsonify(summary)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/low_stock')
def low_stock_alert():
    """API endpoint for low stock alerts"""
    try:
        threshold = request.args.get('threshold', 5, type=int)
        low_stock_items = excel_handler.get_low_stock_items(threshold)
        return jsonify(low_stock_items)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)