// Main JavaScript functionality for MetroPos
class MetroPos {
    constructor() {
        this.cart = [];
        this.currentProduct = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadCartFromStorage();
    }

    setupEventListeners() {
        // Keyboard dialog events
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('key')) {
                this.handleKeyPress(e.target);
            }
        });

        // Cart events
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('remove-item')) {
                this.removeFromCart(e.target);
            }
        });

        // Form validation
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            form.addEventListener('submit', this.validateForm);
        });
    }

    // Keyboard functionality
    handleKeyPress(keyElement) {
        const value = keyElement.textContent;
        const screen = document.getElementById('screen');
        
        if (!screen) return;

        if (value === '清除') {
            screen.textContent = '0';
        } else if (value === '确定') {
            this.submitQuantity();
        } else if (!isNaN(value)) {
            if (screen.textContent === '0') {
                screen.textContent = value;
            } else {
                screen.textContent += value;
            }
        }
    }

    // Product selection
    openQuantityDialog(productName, productStock) {
        this.currentProduct = {
            name: productName,
            stock: parseInt(productStock)
        };
        
        const dialog = document.getElementById('quantity-dialog');
        if (dialog) {
            dialog.style.display = 'block';
            document.getElementById('screen').textContent = '0';
        }
    }

    submitQuantity() {
        const screen = document.getElementById('screen');
        const quantity = parseInt(screen.textContent);
        
        if (!this.currentProduct || quantity <= 0) {
            return;
        }

        if (quantity > this.currentProduct.stock) {
            this.showAlert('库存不足，无法添加到购物车。', 'warning');
            return;
        }

        this.addToCart(this.currentProduct.name, quantity);
        this.closeQuantityDialog();
    }

    closeQuantityDialog() {
        const dialog = document.getElementById('quantity-dialog');
        if (dialog) {
            dialog.style.display = 'none';
        }
        this.currentProduct = null;
    }

    // Cart management
    addToCart(productName, quantity) {
        const existingItem = this.cart.find(item => item.name === productName);
        
        if (existingItem) {
            existingItem.quantity += quantity;
        } else {
            this.cart.push({ name: productName, quantity: quantity });
        }
        
        this.updateCartDisplay();
        this.saveCartToStorage();
        this.showAlert(`已添加 ${productName} x${quantity} 到购物车`, 'success');
    }

    removeFromCart(element) {
        const cartItem = element.closest('.cart-item');
        const productName = cartItem.querySelector('span').textContent.split(' - ')[0];
        
        this.cart = this.cart.filter(item => item.name !== productName);
        cartItem.remove();
        this.saveCartToStorage();
    }

    updateCartDisplay() {
        const cartItems = document.getElementById('cart-items');
        if (!cartItems) return;

        cartItems.innerHTML = '';
        
        this.cart.forEach(item => {
            const cartItem = document.createElement('div');
            cartItem.className = 'cart-item';
            cartItem.innerHTML = `
                <span>${item.name} - ${item.quantity}</span>
                <span class="remove-item" title="移除商品">×</span>
            `;
            cartItems.appendChild(cartItem);
        });
    }

    // Storage management
    saveCartToStorage() {
        localStorage.setItem('metropos_cart', JSON.stringify(this.cart));
    }

    loadCartFromStorage() {
        const savedCart = localStorage.getItem('metropos_cart');
        if (savedCart) {
            this.cart = JSON.parse(savedCart);
            this.updateCartDisplay();
        }
    }

    clearCart() {
        this.cart = [];
        this.updateCartDisplay();
        this.saveCartToStorage();
    }

    // Shipment processing
    async submitCart() {
        if (this.cart.length === 0) {
            this.showAlert('购物车为空!', 'warning');
            return;
        }

        try {
            const response = await fetch('/shipment_confirmation', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    products: this.cart
                })
            });

            if (response.ok) {
                const html = await response.text();
                document.open();
                document.write(html);
                document.close();
                this.clearCart();
            } else {
                throw new Error(`Request failed with status ${response.status}`);
            }
        } catch (error) {
            console.error('Error:', error);
            this.showAlert('提交失败，请重试！', 'error');
        }
    }

    // Utility functions
    showAlert(message, type = 'info') {
        // Create alert element
        const alert = document.createElement('div');
        alert.className = `alert alert-${type}`;
        alert.textContent = message;
        alert.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 5px;
            color: white;
            z-index: 10000;
            font-weight: bold;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        `;

        // Set background color based on type
        const colors = {
            success: '#28a745',
            warning: '#ffc107',
            error: '#dc3545',
            info: '#17a2b8'
        };
        alert.style.backgroundColor = colors[type] || colors.info;

        document.body.appendChild(alert);

        // Auto remove after 3 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                alert.parentNode.removeChild(alert);
            }
        }, 3000);
    }

    validateForm(event) {
        const form = event.target;
        const requiredFields = form.querySelectorAll('[required]');
        let isValid = true;

        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                field.style.borderColor = '#dc3545';
                isValid = false;
            } else {
                field.style.borderColor = '#ced4da';
            }
        });

        if (!isValid) {
            event.preventDefault();
            this.showAlert('请填写所有必填字段', 'warning');
        }
    }

    // Print functionality
    printPage() {
        window.print();
    }

    // Navigation helpers
    goBack() {
        window.history.back();
    }

    goForward() {
        window.history.forward();
    }

    refreshPage() {
        window.location.reload();
    }
}

// Initialize MetroPos when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.metropos = new MetroPos();
});

// Global functions for backward compatibility
function openQuantityDialog(productName, productStock) {
    window.metropos.openQuantityDialog(productName, productStock);
}

function addToScreen(value) {
    const screen = document.getElementById('screen');
    if (screen) {
        if (screen.textContent === '0') {
            screen.textContent = value;
        } else {
            screen.textContent += value;
        }
    }
}

function clearScreen() {
    const screen = document.getElementById('screen');
    if (screen) {
        screen.textContent = '0';
    }
}

function submitQuantity() {
    window.metropos.submitQuantity();
}

function submitCart() {
    window.metropos.submitCart();
}

function printPage() {
    window.metropos.printPage();
}