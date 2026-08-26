let scannerReader
let scanning = false

function getScannerStatus() {
    return document.getElementById("scanner-status")
}

function setScannerStatus(message, type = "info") {
    const scannerStatus = getScannerStatus()
    if (!scannerStatus) return

    scannerStatus.textContent = message
    scannerStatus.className = `alert alert-${type} py-2 mb-2`
    scannerStatus.hidden = !message
}

function toggleScanner(){

    const container = document.getElementById("scanner-container")

    if(!scanning){
        container.style.display = "block"
        startScanner()
    } else {
        stopScanner()
    }
}

function startScanner(){
    const Reader = window.Html5Qrcode
    const readerElement = document.getElementById("scanner-reader")

    if (!Reader || !readerElement) {
        setScannerStatus("Scanner indisponível. Insira o código manualmente.", "warning")
        return
    }

    scannerReader = new Reader("scanner-reader")
    scanning = true
    setScannerStatus("Aponte a câmera para o código de barras.", "info")

    scannerReader.start(
        { facingMode: "environment" },
        { fps: 10, qrbox: { width: 280, height: 140 } },
        (codigo) => {
            document.getElementById("barcode-input").value = codigo
            buscarProduto(codigo)
            stopScanner()
        },
        () => {}
    ).catch(() => {
        setScannerStatus("Não foi possível acessar a câmera. Insira o código manualmente.", "warning")
        stopScanner()
    })
}

async function stopScanner(){
    if (scannerReader) {
        try {
            if (scannerReader.isScanning) await scannerReader.stop()
            scannerReader.clear()
        } catch {}
    }
    scannerReader = null
    scanning = false
    const container = document.getElementById("scanner-container")
    if (container) container.style.display = "none"
}

async function buscarProduto(codigo){
    const normalizedCode = codigo.trim()
    if (!normalizedCode) {
        setScannerStatus("Insira um código de barras válido.", "warning")
        return
    }

    setScannerStatus("Consultando produto...", "info")

    try {
        const produto = await buscarEmCatalogos(normalizedCode)

        if(produto){
            preencherProduto(produto)
            setScannerStatus("Produto encontrado. Confira os dados antes de guardar.", "success")
        } else {
            setScannerStatus("Código não encontrado. Confira o código ou preencha os dados manualmente.", "warning")
        }
    } catch {
        setScannerStatus("Não foi possível consultar o produto. Verifique a conexão ou preencha os dados manualmente.", "warning")
    }
}

async function buscarEmCatalogos(codigo) {
    const consultas = [
        { nome: "produtos gerais", consultar: async () => {
            const response = await fetch(
                "https://world.openproductsfacts.org/api/v2/product/" + encodeURIComponent(codigo) + ".json?fields=product_name,product_name_pt,product_name_en,brands,generic_name,categories"
            )
            if (!response.ok) throw new Error("Falha na consulta de produtos")
            const data = await response.json()
            if (data.status !== 1 || !data.product) return null

            const produto = data.product

            return {
                nome: produto.product_name || produto.product_name_pt || produto.product_name_en,
                descricao: [produto.brands, produto.generic_name, produto.categories].filter(Boolean).join(" — ")
            }
        }},
        { nome: "cosméticos", consultar: async () => {
            const response = await fetch(
                "https://world.openbeautyfacts.org/api/v2/product/" + encodeURIComponent(codigo) + ".json?fields=product_name,product_name_pt,product_name_en,brands,generic_name,categories"
            )
            if (!response.ok) throw new Error("Falha na consulta de cosméticos")
            const data = await response.json()
            if (data.status !== 1 || !data.product) return null

            const produto = data.product
            return {
                nome: produto.product_name || produto.product_name_pt || produto.product_name_en,
                descricao: [produto.brands, produto.generic_name, produto.categories].filter(Boolean).join(" — ")
            }
        }},
        { nome: "produtos para animais", consultar: async () => {
            const response = await fetch(
                "https://world.openpetfoodfacts.org/api/v2/product/" + encodeURIComponent(codigo) + ".json?fields=product_name,product_name_en,brands,generic_name,categories"
            )
            if (!response.ok) throw new Error("Falha na consulta de produtos para animais")
            const data = await response.json()
            if (data.status !== 1 || !data.product) return null

            const produto = data.product
            return {
                nome: produto.product_name || produto.product_name_en,
                descricao: [produto.brands, produto.generic_name, produto.categories].filter(Boolean).join(" — ")
            }
        }},
        { nome: "alimentos", consultar: async () => {
            const response = await fetch(
                "https://world.openfoodfacts.org/api/v2/product/" + encodeURIComponent(codigo) + ".json?fields=product_name,product_name_pt,brands,generic_name"
            )
            if (!response.ok) throw new Error("Falha na consulta de alimentos")
            const data = await response.json()
            if (data.status !== 1) return null

            return {
                nome: data.product.product_name || data.product.product_name_pt,
                descricao: data.product.brands || data.product.generic_name || ""
            }
        }}
    ]

    for (const consulta of consultas) {
        setScannerStatus(`Procurando em ${consulta.nome}...`, "info")
        try {
            const produto = await consulta.consultar()
            if (produto?.nome) return produto
        } catch {}
    }

    return null
}

function buscarProdutoManual() {
    buscarProduto(document.getElementById("barcode-input").value)
}
function preencherProduto(produto){

    setTimeout(() => {

        const form = document.querySelector("[data-barcode-form]")
        const nome = form?.querySelector("input[name='nome']")
        const descricao = form?.querySelector("textarea[name='descricao']")

        if(nome){
            nome.value = produto.nome || "Produto"
        }

        if(descricao){
            descricao.value = produto.descricao || ""
        }

    }, 200)
}
