function showLoading() {
    const styles = `background: rgba(0, 0, 0, 0.4);
    position: fixed;
    top: 0;
    left: 0;
    bottom: 0;
    right: 0;
    overflow: auto;
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 100;
    `;

    document.body.insertAdjacentHTML('beforeend',`<div style="${styles}" class="loading">
            <img src="/static/img/loading.svg"/>
        </div>`)
}

function closeLoading() {
    document.querySelector('.loading').remove();
}
