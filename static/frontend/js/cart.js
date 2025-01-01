const isAuthenticated = document.body.dataset.auth === 'true';

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function updateCartCount(count) {
    // Update all cart count elements including the header
    const cartCountElements = document.querySelectorAll('.cart-count, .cart-item-count');
    cartCountElements.forEach(element => {
        element.textContent = count;
    });
}

function formatPrice(price) {
    return '৳' + parseFloat(price).toFixed(2);
}

function updateCartDisplay(cartData) {
    const cartItemsContainer = document.querySelector('.side-cart-items');
    const cartTotalElement = document.querySelector('.main-total-cart span');
    const cartCountElement = document.querySelector('.main-cart-title span');
    
    // Update cart count in header
    cartCountElement.textContent = `(${cartData.total_items} Items)`;
    
    // Clear existing items
    cartItemsContainer.innerHTML = '';
    
    // Add each item to the cart display
    cartData.items.forEach(item => {
        const product = item.product;
        const itemHtml = `
            <div class="cart-item" data-item-id="${item.id}">
                <div class="cart-product-img">
                    ${product.primary_image ? 
                        `<img src="${product.primary_image.image}" alt="${product.name}">` :
                        '<img src="https://via.placeholder.com/150x150?text=No+Image" alt="Default Image">'
                    }
                </div>
                <div class="cart-text">
                    <h4>${product.name}</h4>
                    <div class="qty-group">
                        <div class="quantity buttons_added">
                            <input type="button" value="-" class="minus minus-btn" data-item="${item.id}">
                            <input type="number" step="1" name="quantity" value="${item.quantity}" 
                                   class="input-text qty text" data-item="${item.id}">
                            <input type="button" value="+" class="plus plus-btn" data-item="${item.id}">
                        </div>
                        <div class="cart-item-price">
                            ${formatPrice(product.selling_price)}
                            ${product.discount_percentage > 0 ? 
                                `<span>${formatPrice(product.original_price)}</span>` : 
                                ''
                            }
                        </div>
                    </div>
                    <button type="button" class="cart-close-btn" data-item="${item.id}">
                        <i class="uil uil-multiply"></i>
                    </button>
                </div>
            </div>
        `;
        cartItemsContainer.insertAdjacentHTML('beforeend', itemHtml);
    });
    
    // Update total price
    cartTotalElement.textContent = formatPrice(cartData.total_price);
    
    // Setup quantity controls after updating display
    setupQuantityControls();
}

function fetchCartItems() {
    if (!isAuthenticated) {
        return;
    }
    fetch('/cart/api/list/')
        .then(response => response.json())
        .then(data => {
            if (data.length > 0) {
                updateCartDisplay(data[0]);
                updateCartCount(data[0].total_items);
            }
        })
        .catch(error => console.error('Error fetching cart:', error));
}

document.addEventListener('DOMContentLoaded', function() {
    // Remove any existing click handlers from cart elements
    const existingCartElements = document.querySelectorAll('.cart-close-btn, .minus-btn, .plus-btn');
    existingCartElements.forEach(element => {
        element.replaceWith(element.cloneNode(true));
    });
    
    // Initialize cart
    fetchCartItems();
    
    // Setup add to cart button
    const addToCartBtns = document.querySelectorAll('.add-cart-btn, .add-to-cart-btn');
    if (addToCartBtns.length > 0) {
        addToCartBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                if (!isAuthenticated) {
                    Swal.fire({
                        icon: 'warning',
                        title: 'Please Login',
                        text: 'You need to login first to add items to cart',
                        showCancelButton: true,
                        confirmButtonText: 'Login',
                        cancelButtonText: 'Cancel',
                        customClass: {
                            container: 'swal-container-class',
                            popup: 'swal-popup-class'
                        }
                    }).then((result) => {
                        if (result.isConfirmed) {
                            window.location.href = '/users/login/';
                        }
                    });
                    return;
                }

                const productId = this.dataset.product;
                const quantityInput = this.closest('.product-item')?.querySelector('.qty.text');
                const quantity = parseInt(quantityInput?.value || 1);

                fetch('/cart/api/add/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify({
                        product_id: productId,
                        quantity: quantity
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        Swal.fire({
                            icon: 'error',
                            title: 'Oops...',
                            text: data.error,
                            customClass: {
                                container: 'swal-container-class',
                                popup: 'swal-popup-class'
                            }
                        });
                    } else {
                        Swal.fire({
                            icon: 'success',
                            title: 'Success!',
                            text: 'Item added to cart',
                            timer: 1500,
                            customClass: {
                                container: 'swal-container-class',
                                popup: 'swal-popup-class'
                            }
                        });
                        updateCartCount(data.cart_total);
                        fetchCartItems(); // Refresh cart display
                    }
                })
                .catch(error => {
                    Swal.fire({
                        icon: 'error',
                        title: 'Oops...',
                        text: 'Something went wrong! Please try again.',
                        customClass: {
                            container: 'swal-container-class',
                            popup: 'swal-popup-class'
                        }
                    });
                });
            });
        });
    }
});

function handleQuantityUpdate(itemId, newQuantity) {
    // Store the original quantity input element
    const quantityInput = document.querySelector(`input.qty.text[data-item="${itemId}"]`);
    const originalValue = parseInt(quantityInput.value);

    fetch('/cart/api/update/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            item_id: itemId,
            quantity: newQuantity
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            // Reset to original value if there's an error
            quantityInput.value = originalValue;
            Swal.fire({
                icon: 'error',
                title: 'Oops...',
                text: data.error,
                customClass: {
                    container: 'swal-container-class',
                    popup: 'swal-popup-class'
                }
            });
        } else {
            if (data.message === 'Item removed from cart') {
                Swal.fire({
                    icon: 'success',
                    title: 'Success!',
                    text: 'Item removed from cart',
                    timer: 1500,
                    customClass: {
                        container: 'swal-container-class',
                        popup: 'swal-popup-class'
                    }
                });
                fetchCartItems(); // Refresh entire cart
            } else {
                // Update quantity input with the server's value
                quantityInput.value = newQuantity;
                
                // Update the specific item's subtotal
                const itemPrice = quantityInput
                    .closest('.cart-text')
                    .querySelector('.cart-item-price');
                itemPrice.innerHTML = formatPrice(data.item_subtotal);
                
                // Update cart total
                const cartTotalElement = document.querySelector('.main-total-cart span');
                cartTotalElement.textContent = formatPrice(data.cart_total_price);
                
                // Update cart count in header
                updateCartCount(data.cart_total);
            }
        }
    })
    .catch(error => {
        // Reset to original value if there's an error
        quantityInput.value = originalValue;
        console.error('Error:', error);
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'Something went wrong! Please try again.',
            customClass: {
                container: 'swal-container-class',
                popup: 'swal-popup-class'
            }
        });
    });
}

function setupQuantityControls() {
    const cartItemsContainer = document.querySelector('.side-cart-items');
    
    cartItemsContainer.addEventListener('click', function(e) {
        e.preventDefault(); // Prevent default form submissions
        const target = e.target;
        
        // Handle remove button click
        if (target.classList.contains('cart-close-btn') || 
            (target.parentElement && target.parentElement.classList.contains('cart-close-btn'))) {
            e.stopPropagation(); // Stop event bubbling
            const button = target.classList.contains('cart-close-btn') ? target : target.parentElement;
            const itemId = button.dataset.item;
            
            if (!itemId) {
                console.error('No item ID found for remove button');
                return;
            }
            
            Swal.fire({
                title: 'Remove Item?',
                text: "Do you want to remove this item from cart?",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#3085d6',
                cancelButtonColor: '#d33',
                confirmButtonText: 'Yes, remove it!',
                customClass: {
                    container: 'swal-container-class',
                    popup: 'swal-popup-class'
                }
            }).then((result) => {
                if (result.isConfirmed) {
                    handleQuantityUpdate(itemId, 0);
                }
            });
            return;
        }
        
        // Handle minus button
        if (target.classList.contains('minus-btn')) {
            const itemId = target.dataset.item;
            const quantityInput = target.nextElementSibling;
            const currentValue = parseInt(quantityInput.value);
            if (currentValue > 1) {
                handleQuantityUpdate(itemId, currentValue - 1);
            } else if (currentValue === 1) {
                // Show confirmation before removing item
                Swal.fire({
                    title: 'Remove Item?',
                    text: "Do you want to remove this item from cart?",
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonColor: '#3085d6',
                    cancelButtonColor: '#d33',
                    confirmButtonText: 'Yes, remove it!',
                    customClass: {
                        container: 'swal-container-class',
                        popup: 'swal-popup-class'
                    }
                }).then((result) => {
                    if (result.isConfirmed) {
                        handleQuantityUpdate(itemId, 0);
                    }
                });
            }
        }
        
        // Handle plus button
        if (target.classList.contains('plus-btn')) {
            const itemId = target.dataset.item;
            const quantityInput = target.previousElementSibling;
            const currentValue = parseInt(quantityInput.value);
            handleQuantityUpdate(itemId, currentValue + 1);
        }
    });

    // Handle direct input changes
    cartItemsContainer.addEventListener('change', function(e) {
        const target = e.target;
        if (target.classList.contains('qty') && target.classList.contains('text')) {
            const itemId = target.dataset.item;
            const newValue = parseInt(target.value);
            if (newValue < 1) {
                handleQuantityUpdate(itemId, 1);
            } else {
                handleQuantityUpdate(itemId, newValue);
            }
        }
    });
}
