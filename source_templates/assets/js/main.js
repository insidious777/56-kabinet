document.addEventListener('DOMContentLoaded',()=>{
    const modal = document.querySelector('.modal');
    const addToCartButtons = document.querySelectorAll('.add-to-card-button');
    const additionsButton = document.querySelector('.modal-additions');
    const incrementButton =  document.querySelector('.count-box-plus');
    const decrementButton =  document.querySelector('.count-box-minus');
    const additionsList =  document.querySelector('.modal-additions-list');

    additionsButton.addEventListener('click',() => {
        if(additionsList.style.display === 'none'){
            additionsList.style.display = 'block';
        }else additionsList.style.display = 'none';
    })

    incrementButton.addEventListener('click',(e) => {
        const itemCount =  document.querySelector('.count-box-number');
        //const price =  document.querySelector('.modal-price');
        itemCount.innerHTML = +itemCount.innerHTML + 1;
        //price.innerHTML = price.innerHTML
    })

    decrementButton.addEventListener('click',(e) => {
        const itemCount =  document.querySelector('.count-box-number');
        const price =  document.querySelector('.modal-price');
        if(+itemCount.innerHTML>1) itemCount.innerHTML = +itemCount.innerHTML - 1;
    })

    modal.addEventListener('click',(e)=>{
        const className = e.target.classList[0];
        if(className === 'modal' || className === 'far') closeModalWindow();
    })

    addToCartButtons.forEach(button => {
        button.addEventListener('click', (e) => {openModalWindow(e)})
    })

    const openModalWindow = (e) => {
        modal.style.display = 'flex';
    }

    const closeModalWindow = () => {
        modal.style.display = 'none';
    }


})