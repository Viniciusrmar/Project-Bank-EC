// --- CONFIGURAÇÃO E ESTADO ---
const API_BASE_URL = 'http://localhost:5000';
let currentUser = null;

// --- NAVEGAÇÃO SPA ---
function showSection(sectionId) {
    document.querySelectorAll('section').forEach(s => s.classList.add('hidden'));
    document.getElementById(sectionId).classList.remove('hidden');
}

function switchTab(tabId) {
    document.querySelectorAll('.dashboard-tab').forEach(t => t.classList.add('hidden'));
    document.querySelectorAll('.nav-links li').forEach(l => l.classList.remove('active'));
    
    document.getElementById(tabId).classList.remove('hidden');
    event.currentTarget.classList.add('active');

    // Carregar dados específicos ao mudar de aba
    if(tabId === 'tab-transacoes') fetchTransacoes();
    if(tabId === 'tab-gastos') fetchGastos();
    if(tabId === 'tab-investimentos') fetchInvestimentos();
}

// --- UTILS ---
function togglePassword() {
    const input = this.previousElementSibling;
    const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
    input.setAttribute('type', type);
    this.classList.toggle('fa-eye-slash');
}

function showToast(msg, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerText = msg;
    document.getElementById('toast-container').appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

// --- VALIDAÇÕES ---
function validarCPF(cpf) {
    cpf = cpf.replace(/[^\d]+/g,'');
    if(cpf.length !== 11) return false;
    // Lógica simplificada: para fins de faculdade, validamos apenas o tamanho.
    // Em produção, deve-se adicionar o cálculo dos dígitos verificadores.
    return true;
}

function calcularIdade(data) {
    const hoje = new Date();
    const nasc = new Date(data);
    let idade = hoje.getFullYear() - nasc.getFullYear();
    const m = hoje.getMonth() - nasc.getMonth();
    if (m < 0 || (m === 0 && hoje.getDate() < nasc.getDate())) idade--;
    return idade;
}

// --- BUSCA CEP ---
document.getElementById('reg-cep').addEventListener('blur', async (e) => {
    const cep = e.target.value.replace(/\D/g, '');
    if (cep.length === 8) {
        try {
            const resp = await fetch(`https://viacep.com.br/ws/${cep}/json/`);
            const data = await resp.json();
            if (!data.erro) {
                document.getElementById('reg-logradouro').value = data.logradouro;
                document.getElementById('reg-bairro').value = data.bairro;
                document.getElementById('reg-cidade').value = data.localidade;
                document.getElementById('reg-estado').value = data.uf;
            }
        } catch (err) { console.error("Erro ao buscar CEP"); }
    }
});

// --- CADASTRO ---
document.getElementById('form-register').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const senha = document.getElementById('reg-password').value;
    const confirma = document.getElementById('reg-confirm-password').value;
    const nascimento = document.getElementById('reg-nascimento').value;
    const cpf = document.getElementById('reg-cpf').value;

    // Reset erros
    document.querySelectorAll('.error-msg').forEach(el => el.innerText = '');

    let hasError = false;

    if (senha !== confirma) {
        showToast("Senhas não conferem", "danger");
        hasError = true;
    }

    if (calcularIdade(nascimento) < 18) {
        showToast("Necessário ser maior de 18 anos", "danger");
        hasError = true;
    }

    if (!validarCPF(cpf)) {
        showToast("CPF inválido", "danger");
        hasError = true;
    }

    if (hasError) return;

    const payload = {
    nome: document.getElementById('reg-nome').value.trim(),
    email: document.getElementById('reg-email').value.trim(),
    senha: senha,
    data_nascimento: nascimento,
    cpf: cpf.replace(/\D/g, ''),
    cep: document.getElementById('reg-cep').value.trim(),
    logradouro: document.getElementById('reg-logradouro').value.trim(),
    numero: document.getElementById('reg-numero').value.trim(),
    bairro: document.getElementById('reg-bairro').value.trim(),
    cidade: document.getElementById('reg-cidade').value.trim(),
    estado: document.getElementById('reg-estado').value.trim()
};

    try {
        const response = await fetch(`${API_BASE_URL}/usuarios/cadastro`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            showToast("Cadastro realizado!");
            showSection('auth-login');
        } else {
            showToast("Erro no cadastro", "danger");
        }
    } catch (err) {
        showToast("Sem conexão com o servidor", "danger");
    }
});

// --- LOGIN ---
document.getElementById('form-login').addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = document.getElementById('login-email').value;
    const senha = document.getElementById('login-password').value;

    try {
        const response = await fetch(`${API_BASE_URL}/usuarios/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, senha })
        });

        const data = await response.json();
        if (response.ok) {
            currentUser = data; // Supõe que o backend retorna { id, nome, email... }
            document.getElementById('user-display-name').innerText = data.nome.split(' ')[0];
            showSection('main-dashboard');
            loadDashboardData();
        } else {
            showToast("E-mail ou senha inválidos", "danger");
        }
    } catch (err) {
        showToast("Erro ao conectar com API", "danger");
    }
});

// --- DASHBOARD E CARREGAMENTO ---
async function loadDashboardData() {
    try {
        const resp = await fetch(`${API_BASE_URL}/contas/usuario/${currentUser.id}`);
        const conta = await resp.json();
        document.getElementById('balance-value').innerText = `R$ ${conta.saldo.toLocaleString('pt-BR', {minimumFractionDigits: 2})}`;
        fetchTransacoes();
    } catch (err) { console.error("Erro dashboard", err); }
}

async function fetchTransacoes() {
    const list = document.getElementById('list-transacoes');
    list.innerHTML = 'Carregando...';
    try {
        // Exemplo: pegamos o ID da conta do usuário guardado no login
        const resp = await fetch(`${API_BASE_URL}/transacoes/conta/${currentUser.contaId}`);
        const trans = await resp.json();
        
        list.innerHTML = trans.map(t => `
            <div class="list-item">
                <div class="item-info">
                    <h4>${t.descricao}</h4>
                    <p>${new Date(t.data).toLocaleDateString()}</p>
                </div>
                <span class="amount ${t.tipo === 'entrada' ? 'positive' : 'negative'}">
                    ${t.tipo === 'entrada' ? '+' : '-'} R$ ${t.valor.toFixed(2)}
                </span>
            </div>
        `).join('');
    } catch (e) { list.innerHTML = 'Nenhuma transação encontrada.'; }
}

// Funções similares para Gastos e Investimentos seguindo a lógica acima...

// --- MODAIS ---
function openModal(modalId) {
    document.getElementById('modal-overlay').classList.remove('hidden');
    document.getElementById(modalId).classList.remove('hidden');
}

function closeModal() {
    document.getElementById('modal-overlay').classList.add('hidden');
    document.querySelectorAll('.modal').forEach(m => m.classList.add('hidden'));
}

// --- SUBMIT TRANSAÇÃO (EXEMPLO) ---
document.getElementById('form-transacao').addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
        conta_id: currentUser.contaId,
        descricao: document.getElementById('trans-descricao').value,
        valor: parseFloat(document.getElementById('trans-valor').value),
        tipo: document.getElementById('trans-tipo').value
    };

    const resp = await fetch(`${API_BASE_URL}/transacoes`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });

    if (resp.ok) {
        showToast("Sucesso!");
        closeModal();
        loadDashboardData();
        fetchTransacoes();
    }
});

function logout() {
    currentUser = null;
    showSection('auth-login');
}

// Iniciar eventos de olho na senha
document.querySelectorAll('.toggle-password').forEach(btn => {
    btn.addEventListener('click', togglePassword);
});