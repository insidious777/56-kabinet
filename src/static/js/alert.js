function showAlert(text, color) {
    const styles = `padding: 15px 35px;
    position: fixed;
    background-color: #F9F4F2;
    border: 1px solid ${color || '#9E421B'};
    border-radius: 2px;
    bottom: 30px;
    left: 50%;
    transform: translateX(-50%);
    color: ${color || '#9E421B'};
    min-width:60vw;
    text-align:center;
    font-weight:bold;
    `;

    document.body.insertAdjacentHTML('beforeend',`<div style="${styles}" class="alert">
                <p>${text}</p>
        </div>`)
    setTimeout(closeAlert, 3000);
}

function closeAlert() {
    document.querySelector('.alert').remove();
}
