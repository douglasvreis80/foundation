const { Client } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const axios = require('axios');
require('dotenv').config(); // Carrega variáveis de ambiente do arquivo .env

const client = new Client({
    puppeteer: {
        args: ['--no-sandbox', '--disable-setuid-sandbox'],
    }
});

const API_URL = process.env.API_URL; // URL da API a partir da variável de ambiente

client.on('ready', () => {
    console.log('FuteBOT is ready!');
});

client.on('qr', qr => {
    qrcode.generate(qr, { small: true });
});

// Função para adicionar jogador
async function adicionarJogador(nome, posicao, eventoId, msg) {
    try {
        const response = await axios.post(`${API_URL}/jogador`, {
            nome,
            posicao,
            evento_id: eventoId,
        });
        msg.reply(`Jogador ${nome} adicionado com sucesso como ${posicao}.`);
    } catch (error) {
        console.error(error);
        msg.reply('Erro ao adicionar jogador. Verifique o servidor.');
    }
}

// Função para remover jogador
async function removerJogador(nome, eventoId, msg) {
    try {
        const response = await axios.delete(`${API_URL}/jogador`, {
            data: {
                nome,
                evento_id: eventoId,
            },
        });
        msg.reply(`Jogador ${nome} removido com sucesso.`);
    } catch (error) {
        console.error(error);
        msg.reply('Erro ao remover jogador. Verifique o servidor.');
    }
}

// Função para listar detalhes da partida
async function listarDetalhesPartida(eventoId, msg) {
    try {
        const response = await axios.get(`${API_URL}/evento/${eventoId}`);
        const { data, hora, jogadores, local } = response.data;

        const detalhes = `
🏟️ *Detalhes da Partida:*
📅 Data: ${data}
⏰ Hora: ${hora}
📍 Local: ${local}

👥 *Jogadores:*
- Principais:
${jogadores.principais.length > 0 ? jogadores.principais.map(j => `  - ${j}`).join('\n') : '  Nenhum'}

- Goleiros:
${jogadores.goleiros.length > 0 ? jogadores.goleiros.map(g => `  - ${g}`).join('\n') : '  Nenhum'}

- Espera:
${jogadores.espera.length > 0 ? jogadores.espera.map(e => `  - ${e}`).join('\n') : '  Nenhum'}
        `;

        msg.reply(detalhes.trim());
    } catch (error) {
        console.error(error);
        msg.reply('Erro ao obter os detalhes da partida. Verifique o servidor.');
    }
}

// Event listeners para os comandos
client.on('message', async msg => {
    const eventoId = 1; // ID fixo para o evento

    if (msg.body === '!ping') {
        msg.reply('pong');
    }

    if (msg.body === '!dentro') {
        const nome = msg.author || 'Jogador Desconhecido';
        await adicionarJogador(nome, 'jogador', eventoId, msg);
    }

    if (msg.body === '!fora') {
        const nome = msg.author || 'Jogador Desconhecido';
        await removerJogador(nome, eventoId, msg);
    }

    if (msg.body === '!goleiro') {
        const nome = msg.author || 'Jogador Desconhecido';
        await adicionarJogador(nome, 'goleiro', eventoId, msg);
    }

    if (msg.body === '!lista') {
        msg.reply('Buscando os detalhes da partida...');
        await listarDetalhesPartida(eventoId, msg);
    }
});

// Inicializa o cliente
client.initialize();
