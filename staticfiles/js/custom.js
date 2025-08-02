function generateToken() {
    const token = [...Array(40)].map(() => Math.floor(Math.random() * 16).toString(16)).join('');
    const input = document.getElementById("id_webhook_secret");
    if (input) {
        input.value = token;
    } else {
        alert('Campo webhook_secret não encontrado!');
    }
}

function copyToClipboard(elementId) {
    const text = document.getElementById(elementId).textContent;
    navigator.clipboard.writeText(text).then(() => {
        alert('URL copiada para a área de transferência!');
    }).catch(() => {
        alert('Falha ao copiar a URL.');
    });
}
