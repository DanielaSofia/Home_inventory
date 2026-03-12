document.addEventListener("DOMContentLoaded", function () {

    const modal = document.getElementById("barcodeModal")

    modal.addEventListener("shown.bs.modal", startScanner)

})

let codeReader

function startScanner() {

    codeReader = new ZXing.BrowserBarcodeReader()
    const video = document.getElementById("scanner-video")
    codeReader.decodeFromVideoDevice(null, video, (result, err) => {

        if (result) {
            let codigo = result.text
            console.log("Código:", codigo)
            buscarProduto(codigo)
            codeReader.reset()
        }
    })
}

function buscarProduto(codigo) {

    fetch("https://world.openfoodfacts.org/api/v0/product/" + codigo + ".json")

        .then(res => res.json())

        .then(data => {

            console.log(data)
            alert("Produto lido")

            if (data.status === 1) {
                alert("Produto Encontrado")

                let produto = data.product

                document.getElementById("id_nome").value =
                    produto.product_name || "Produto"

                document.getElementById("id_descricao").value =
                    produto.brands || ""

            }

            else {

                alert("Produto não encontrado")

            }

        })

}