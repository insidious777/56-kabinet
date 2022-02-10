document.addEventListener('DOMContentLoaded',()=>{
    const modal = document.querySelector('.modal');
    const addToCartButtons = document.querySelectorAll('.add-to-card-button');
    const additionsButton = document.querySelector('.modal-additions');
    const incrementButton = document.querySelector('.count-box-plus');
    const decrementButton = document.querySelector('.count-box-minus');
    const additionsList = document.querySelector('.modal-additions-list');
    const modalAddToCart = document.querySelector('.modal-add-to-cart');
    const menuItems = document.querySelectorAll('.menu-item');
    const isMobile = window.matchMedia("only screen and (max-width:760px)").matches;
    let currentItem, maxWidth = 90;

    if (isMobile) {
        const categoryCartItemText = document.querySelectorAll('.category-card-item-text');
        categoryCartItemText.forEach((el) => {
            el.addEventListener('click', (e) => {
                if (el.children[1].style.display == '') el.children[1].style.display = 'none'
                else el.children[1].style.display = ''
            })
        })
    }

    menuItems.forEach((el) => {
        if (el.href == location.href) {
            el.className += ' menu-item-active';
        }
        if (el.offsetWidth > maxWidth) maxWidth = el.offsetWidth;
    })

    document.querySelectorAll('.menu-item-content').forEach((el) => {
        el.style.width = `${maxWidth}px`;
    })

    modalAddToCart.addEventListener('click', (e) => {
        const menu_item_id = +document.querySelector('.modal-additions').getAttribute('menu_id');
        const count = +document.querySelector('.count-box-number').innerHTML;
        const inputs = document.querySelectorAll('.addition-item-input');
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const checkedInputsId = [];

        inputs.forEach((el) => {
            if (el.checked) checkedInputsId.push(+el.getAttribute('id'));
        })

        fetch(`/api/v1/order/add-to-cart/`, {
            method: 'POST',
            body: JSON.stringify({
                menu_item_id,
                count,
                addition_ids: checkedInputsId
            }),
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            }
        }).then(response => response.json()).then(data => {
            if (data && data.total_amount) {
                document.querySelector('.header-cart-button').classList.remove('d-none');
                document.querySelector('.header-cart-price').innerHTML = data.total_amount + ' грн';
                showAlert('Товар успішно додано до корзини', 'green');
                currentItem.querySelector('.price-section').insertAdjacentHTML('beforeend', `<img class="item-in-cart-icon" src="/static/img/bag1.png">`);
            }
            closeModalWindow();
        });
    })

    additionsButton.addEventListener('click', async (e) => {
        if (additionsList.style.display === 'none') {
            additionsList.style.display = 'block';
        } else {
            additionsList.style.display = 'none';
        }
    })

    incrementButton.addEventListener('click', (e) => {
        const itemCount = document.querySelector('.count-box-number');
        //const price =  document.querySelector('.modal-price');
        itemCount.innerHTML = +itemCount.innerHTML + 1;
        //price.innerHTML = price.innerHTML
    })

    decrementButton.addEventListener('click', (e) => {
        const itemCount = document.querySelector('.count-box-number');
        const price = document.querySelector('.modal-price');
        if (+itemCount.innerHTML > 1) itemCount.innerHTML = +itemCount.innerHTML - 1;
    })

    modal.addEventListener('click', (e) => {
        const className = e.target.classList[0];
        if (className === 'modal' || className === 'far') closeModalWindow();
    })

    addToCartButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            openModalWindow(e)
            currentItem = e.target.parentNode.parentNode;
        });
    })

    const openModalWindow = (e) => {
        const button = e.target.classList[0] === 'add-to-card-button' ? e.target : e.target.parentNode;
        const id = button.getAttribute('menu_id');

        fetch(`/api/v1/menu/menu-items/${id}/additions/`).then(response => response.json()).then(additions => {
            if (additions.length > 0) {
                document.querySelector('.modal-additions').classList.remove('d-none');
                document.querySelector('.additions-box').innerHTML = '';
                additions.forEach((elem) => {
                    appendHtml(
                        document.querySelector('.additions-box'),
                        `<div class="addition-item">
                            <input class="addition-item-input" id="${elem.id}" type="checkbox"/>
                            <label>${elem.title}</label>
                            <p class="addition-price">${elem.price} грн</p>
                        </div>`
                    );
                })
            }
        });
        document.querySelector('.modal-main-img').src = button.parentNode.parentNode.parentNode.children[0].src;

        document.querySelector('.modal-volume').innerHTML = button.parentNode.getElementsByClassName('card-volume')[0].innerHTML;
        document.querySelector('.modal-price').innerHTML = button.parentNode.getElementsByClassName('card-price')[0].innerHTML + " грн";

        document.querySelector('.modal-top-text').children[0].innerHTML = button.parentNode.parentNode.children[0].innerHTML;
        document.querySelector('.modal-top-text').children[1].innerHTML = button.parentNode.children[0].innerHTML;

        document.querySelector('.modal-additions').setAttribute('menu_id', id);
        modal.style.display = 'flex';
    }

    const closeModalWindow = () => {
        modal.style.display = 'none';
        additionsList.style.display = 'none';
        document.querySelector('.count-box-number').innerHTML = '1';
        document.querySelector('.modal-additions').classList.add('d-none');

        document.querySelector('.additions-box').innerHTML = '';


    }

    function appendHtml(el, str) {
        let div = document.createElement('div');
        div.innerHTML = str;
        while (div.children.length > 0) {
            el.appendChild(div.children[0]);
        }
    }

})