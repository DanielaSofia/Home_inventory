let codeReader
let scanning = false

function toggleScanner(){

    const container = document.getElementById("scanner-container")

    if(!scanning){
        container.style.display = "block"
        startScanner()
        scanning = true
    } else {
        stopScanner()
        container.style.display = "none"
        scanning = false
    }
}

function startScanner(){

    codeReader = new ZXing.BrowserBarcodeReader()

    const video = document.getElementById("scanner-video")

    codeReader.decodeFromVideoDevice(null, video, (result, err) => {

        if(result){

            const codigo = result.text

            console.log("Código:", codigo)

            buscarProduto(codigo)

            stopScanner()
        }

    })
}

function stopScanner(){
    if(codeReader){
        codeReader.reset()
    }
}

function buscarProduto(codigo){

    fetch("https://world.openfoodfacts.org/api/v0/product/" + codigo + ".json")
    .then(res => res.json())
    .then(data => {

        if(data.status === 1){

            const produto = data.product
            console.log("Produto encontrado")
            preencherProduto(produto)

        } else {

            console.log("Produto não encontrado")

        }

    })
}
function preencherProduto(produto){

    setTimeout(() => {

        const nome = document.querySelector("#addItemModal input[name='nome']")
        const descricao = document.querySelector("#addItemModal textarea[name='descricao']")

        if(nome){
            nome.value =
                produto.product_name ||
                produto.product_name_pt ||
                "Produto"
        }

        if(descricao){
            descricao.value =
                produto.brands ||
                produto.generic_name ||
                ""
        }

    }, 200)
}
