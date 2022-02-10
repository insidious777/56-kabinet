async function cancelOrder() {
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    fetch(`/api/v1/order/reject/`,{
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        }
    }).then(response => response.json()).then(data => {
        if(data && data.hasOwnProperty('status')){
            if(data.status === "OK") window.location.href = "/";
        }else{
            showAlert('Сталась невідома помилка, будь ласка спробуйте пізніше', 'red');
        }
    }).catch(()=>{
        showAlert('Сталась невідома помилка, будь ласка спробуйте пізніше', 'red');
    });
}