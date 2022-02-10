document.addEventListener('DOMContentLoaded',()=>{
    const itemDeleteButtons = document.querySelectorAll('.item-delete-button');
    const additionDeleteButtons = document.querySelectorAll('.addition-delete-button');
    const plusButtons = document.querySelectorAll('.count-box-plus');
    const minusButtons = document.querySelectorAll('.count-box-minus');
    const clearCartButton = document.querySelector('.clear-cart-button');
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    updatePrice(+document.querySelector('.items-price').innerHTML.replace(/[^0-9]/g,''));
    clearCartButton.addEventListener('click',(e) => {
        fetch(`/api/v1/order/clear/`,{
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            }
        }).then(response => response.json()).then(data => {
            if(data && data.hasOwnProperty('status')){
                document.querySelectorAll('table-item').forEach((el)=>{
                    el.remove();
                })
                updatePrice(0);
                window.location.href = "/";
            }
        }).catch(()=>{
            showAlert('Сталась невідома помилка, будь ласка спробуйте пізніше', 'red');
        });
    })

    minusButtons.forEach((el)=>{
        el.addEventListener('click',(e)=>{
            fetch(`/api/v1/order/decrease-count/`,{
                method: 'POST',
                body: JSON.stringify({
                    cart_item_id: +e.target.parentNode.getAttribute('data-menu-id')
                }),
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                }
            }).then(response => response.json()).then(data => {
                if(data && data.hasOwnProperty('count')){
                    e.target.parentNode.children[1].innerHTML = data.count;
                    e.target.parentNode.parentNode.children[2].children[0].children[0].innerHTML = data.cart_item_total_amount;
                    updatePrice(data.total_amount);
                }
            }).catch(()=>{
                showAlert('Сталась невідома помилка, будь ласка спробуйте пізніше', 'red');
            });
        })
    })


    plusButtons.forEach((el)=>{
        el.addEventListener('click',(e)=>{
            fetch(`/api/v1/order/increase-count/`,{
                method: 'POST',
                body: JSON.stringify({
                    cart_item_id: +e.target.parentNode.getAttribute('data-menu-id')
                }),
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                }
            }).then(response => response.json()).then(data => {
                if(data){
                    e.target.parentNode.children[1].innerHTML = data.count;
                    e.target.parentNode.parentNode.children[2].children[0].children[0].innerHTML = data.cart_item_total_amount;
                    updatePrice(data.total_amount);
                }
            }).catch(()=>{
                showAlert('Сталась невідома помилка, будь ласка спробуйте пізніше', 'red');
            });
        })
    })



    itemDeleteButtons.forEach((el)=>{
        el.addEventListener('click',(e) => {

            fetch(`/api/v1/order/remove-cart-item/`,{
                method: 'POST',
                body: JSON.stringify({
                    cart_item_id: +e.target.getAttribute('data-item-id')
                }),
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                }
            }).then(response => response.json()).then(data => {
                if(data && data.hasOwnProperty('total_amount')){
                    e.target.parentNode.parentNode.parentNode.remove();
                    updatePrice(data.total_amount);
                    if(document.querySelectorAll('.table-item').length === 0) window.location.href = "/";
                }
            }).catch(()=>{
                showAlert('Сталась невідома помилка, будь ласка спробуйте пізніше', 'red');
            });

        })
    })

    additionDeleteButtons.forEach((el)=>{
        el.addEventListener('click',(e)=>{

            fetch(`/api/v1/order/remove-cart-item-addition/`,{
                method: 'POST',
                body: JSON.stringify({
                    cart_item_id: +e.target.getAttribute('data-menu-id'),
                    addition_id: +e.target.getAttribute('data-addition-id')
                }),
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                }
            }).then(response => response.json()).then(data => {
                if(data && data.hasOwnProperty('total_amount')){
                    e.target.parentNode.parentNode.parentNode.parentNode.getElementsByClassName('price-box')[0].children[0].innerHTML = data.cart_item_total_amount;
                    e.target.parentNode.remove();
                    updatePrice(data.total_amount);
                }
            }).catch(()=>{
                showAlert('Сталась невідома помилка, будь ласка спробуйте пізніше', 'red');
            });

        })
    })

    function updatePrice(itemsPrice) {
        const deliveryPrice = +document.querySelector('.delivery-price').innerHTML.replace(/[^0-9]/g,'');

        document.querySelector('.total-price-delivery').innerHTML = (deliveryPrice + itemsPrice) + ' грн';
        document.querySelector('.cart-price-with-delivery').innerHTML = (deliveryPrice + itemsPrice) + ' грн';
        document.querySelector('.total-price').innerHTML = itemsPrice + ' грн';
        document.querySelector('.cart-price-without-delivery').innerHTML = itemsPrice + ' грн';
    }
})