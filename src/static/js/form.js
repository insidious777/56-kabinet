document.addEventListener('DOMContentLoaded',()=>{
    const minOrderCompletionTime = document.querySelector('.min-order-completion-time').innerHTML.split(':')[1];
    const checkoutButton = document.querySelector('.checkout-button');
    let currentDate = new Date();
    const minTime =  new Date(currentDate.getTime() + (minOrderCompletionTime)*60000 + 60000);
    const mask = IMask(document.querySelector('.phone-number-input'), {
        mask: '+{38}({\\0}00)000-00-00'
    });
    const hoursMask = IMask(document.querySelector('.other-time-hours'), {
        mask: IMask.MaskedRange,
        from: 0,
        to: 23,
        maxLength: 2,
    });
    const minutesMask = IMask(document.querySelector('.other-time-minutes'), {
        mask: IMask.MaskedRange,
        from: 0,
        to: 59,
        maxLength: 2,
    });

    hoursMask.value = minTime.getHours().toString();
    minutesMask.value = minTime.getMinutes().toString();
    document.querySelector('.soon-time').innerHTML = `Найближчим часом (${minTime.getHours()}:${minTime.getMinutes()})`;
    document.querySelector('.other-time-input').addEventListener('click',(e)=>{
        if(e.target.checked) document.querySelector('.other-time-colons').style.display = 'flex';
        else document.querySelector('.other-time-colons').style.display = 'none';
    })
    document.querySelector('.soon-time-input').addEventListener('click',(e)=>{
        if(e.target.checked) document.querySelector('.other-time-colons').style.display = 'none';
        else document.querySelector('.other-time-colons').style.display = 'flex';
    })
    const deliveryTypeInputs = document.querySelectorAll('[name=delivery-type-label]');
    const deliveryForm = document.querySelector('.delivery-form');
    let deliveryType = "SELF_PICKUP";
    console.log(deliveryTypeInputs[0])
    deliveryTypeInputs[0].addEventListener('click', (e)=>{
        setTimeout(()=>{
            if(e.target.parentNode.children[0].checked) {
                deliveryType = "COURIER"
                deliveryForm.style.display = 'block';
                document.querySelector('.delivery-courier').style.display = 'block';
                document.querySelector('.delivery-self-pickup').style.display = 'none';
                document.querySelector('.total-price-delivery').style.display = 'block';
                document.querySelector('.total-price').style.display = 'none';
                document.querySelector('.cart-price-with-delivery').style.display = 'block';
                document.querySelector('.cart-price-without-delivery').style.display = 'none';

            }
        },0)
    })

    deliveryTypeInputs[1].addEventListener('click', (e)=>{
        setTimeout(()=> {
            if (e.target.parentNode.children[0].checked) {
                deliveryType = "SELF_PICKUP";
                deliveryForm.style.display = 'none';
                document.querySelector('.delivery-courier').style.display = 'none';
                document.querySelector('.delivery-self-pickup').style.display = 'block';
                document.querySelector('.total-price-delivery').style.display = 'none';
                document.querySelector('.total-price').style.display = 'block';
                document.querySelector('.cart-price-with-delivery').style.display = 'none';
                document.querySelector('.cart-price-without-delivery').style.display = 'block';
            }
        },0)
    })



    // const targetNode = document.querySelector('.total-price');
    // const callback = function(mutationsList, observer) {
    //         console.log(mutationsList[0].target)
    //
    //         if(deliveryType==='COURIER') {
    //             const deliveryCost = document.querySelector('.delivery-courier').innerHTML.replace(/\D/g, "");
    //             mutationsList[0].target.innerHTML= mutationsList[0].target.innerHTML.replace(/\D/g, "")+ deliveryCost + ' грн'
    //         }
    //     };
    // const observer = new MutationObserver(callback);
    // observer.observe(targetNode, { childList: true });




    checkoutButton.addEventListener('click',(e) => {
        showLoading();
        //Start
        e.preventDefault();
        const phoneNumber = mask;
        const name = document.querySelector('.name-input');
        const description = document.querySelector('.description-input').value;
        const otherTimeInput = document.querySelector('.other-time-input');
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const settlement = document.querySelector('.settlement-input');
        const street = document.querySelector('.street-input');
        const building = document.querySelector('.building-number-input');


        const paymentTypesInputs = document.querySelectorAll('.payment-type-input');
        let pickupTime;
        let paymentMethod = "CASH";


        document.querySelector('.phone-number-input').style.border = 'none';
        name.style.border = 'none';
        if(!name.value) {
            showAlert("Введіть ім'я",'red');
            name.style.border = '1px solid red';
            closeLoading();
            return
        }

        if(!phoneNumber.unmaskedValue) {
            showAlert('Введіть номер телефону','red');
            document.querySelector('.phone-number-input').style.border = '1px solid red';
            closeLoading();
            return
        }

        if(deliveryType === "COURIER"){
            settlement.style.border = 'none';
            if(!settlement.value) {
                showAlert('Введіть населенний пункт','red');
                settlement.style.border = '1px solid red';
                closeLoading();
                return
            }

            street.style.border = 'none';
            if(!street.value) {
                showAlert('Введіть вулицю','red');
                street.style.border = '1px solid red';
                closeLoading();
                return
            }

            building.style.border = 'none';
            if(!building.value) {
                showAlert('Введіть № будинку','red');
                building.style.border = '1px solid red';
                closeLoading();
                return
            }
        }


        if(otherTimeInput.checked){
            let currentDate = new Date();
            currentDate.setHours(+hoursMask.value, +minutesMask.value,0, 0);
            pickupTime = new Date(currentDate.getTime() + (minOrderCompletionTime)*60000 + 60000).toISOString().slice(0,-5);
        }else{
            let currentDate = new Date();
            currentDate.setSeconds(0);
            pickupTime = new Date(currentDate.getTime() + (minOrderCompletionTime)*60000 + 60000).toISOString().slice(0,-5);
        }

        paymentTypesInputs.forEach((input)=>{
            if(input.checked) paymentMethod = input.getAttribute('data-payment-type');
        })

        const fetchData = deliveryType==='COURIER'?
            {
                delivery_method: "COURIER",
                payment_method: paymentMethod,
                customer_name: name.value,
                phone_number: '+' + phoneNumber.unmaskedValue,
                customer_comment: description,
                settlement:settlement.value,
                street:street.value,
                building_number: building.value,
                apartment_number: document.querySelector('.apartment-number-input').value,
                entrance_number: document.querySelector('.entrance-number-input').value,
                floor_number: document.querySelector('.floor-number-input').value,
                door_phone_number: document.querySelector('.door-phone-input').value,
                peoples_count: document.querySelector('.peoples-input').value,
            }:
            {
                delivery_method: "SELF_PICKUP",
                self_pickup_time: pickupTime,
                payment_method: paymentMethod,
                customer_name: name.value,
                phone_number: '+' + phoneNumber.unmaskedValue,
                customer_comment: description
            }

        fetch(`/api/v1/order/create/`,{
            method: 'POST',
            body: JSON.stringify(fetchData),
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            }
        }).then(response => response.json()).then(data => {
            closeLoading();
            if(data.phone_number) {
                showAlert('Введіть коректний номер телефону в форматі +38(097)123-45-67','red');
                return;
            }

            if(data.detail && data.detail.code && data.detail.code === 'menu_item_order_not_allowed_at_this_time'){
                showAlert('В вашому кошику знаходяться страви, які мають обмеження по часу','red');
                return;
            }

            if(data.detail && data.detail.code && data.detail.code === 'menu_item_order_not_allowed'){
                showAlert('В вашому кошику знаходяться страви, які мають обмеження по часу','red');
                return;
            }

            if(data.self_pickup_time) {
                let currentDate = new Date();
                const minTime =  new Date(currentDate.getTime() + (minOrderCompletionTime)*60000 + 60000);
                showAlert(`Введенно некоректний час. Час повинен бути не меньший ніж ${minTime}`,'red');
                return;
            }
            if(data && data.hasOwnProperty('payment_required')){
                if(data.payment_required) window.location.href = "/order/payment";
                else {
                    document.querySelector('.success-modal').style.display = 'flex';
                }
            }
        }).catch((e)=>{
                console.log(e);
                closeLoading();
            })

    })
})