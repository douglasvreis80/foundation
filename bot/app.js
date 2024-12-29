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
    console.log('FuteBOT 1 is ready!');
});

client.on('qr', qr => {
    qrcode.generate(qr, { small: true });
});

// Função para adicionar jogador
async function adicionarJogador(nome, posicao, partidaId, msg) {
    try {
        const response = await axios.post(`${API_URL}/jogador`, {
            nome,
            posicao,
            partida_id: partidaId,
        });
        msg.reply(`Jogador ${nome} adicionado com sucesso como ${posicao}.`);
    } catch (error) {
        console.error(error);

        if (error.response && error.response.data && error.response.data.mensagem) {
            // Mensagem de erro retornada pelo servidor
            msg.reply(`Erro: ${error.response.data.mensagem}`);
        } else {
            // Erro genérico (servidor não retornou mensagem)
            msg.reply('Erro ao adicionar jogador. Verifique o servidor.');
        }
    }
}


// Função para remover jogador
async function removerJogador(nome, partidaId, msg) {
    try {
        const response = await axios.delete(`${API_URL}/jogador`, {
            data: {
                nome,
                partida_id: partidaId,
            },
        });
        msg.reply(`Jogador ${nome} removido com sucesso.`);

    } catch (error) {
        console.error(error);

        if (error.response && error.response.data && error.response.data.mensagem) {
            // Mensagem de erro retornada pelo servidor
            msg.reply(`Erro: ${error.response.data.mensagem}`);
        } else {
            // Erro genérico (servidor não retornou mensagem)
            msg.reply('Erro ao adicionar jogador. Verifique o servidor.');
        }
    }
}

// Função para listar detalhes da partida
async function listarDetalhesPartida(partidaId, msg) {
    try {
        const response = await axios.get(`${API_URL}/partida/${partidaId}`);
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

        if (error.response && error.response.data && error.response.data.mensagem) {
            // Mensagem de erro retornada pelo servidor
            msg.reply(`Erro: ${error.response.data.mensagem}`);
        } else {
            // Erro genérico (servidor não retornou mensagem)
            msg.reply('Erro ao adicionar jogador. Verifique o servidor.');
        }
    }
}

// Event listeners para os comandos
client.on('message', async msg => {
    const partidaId = 1; // ID fixo para o partida

    if (msg.body === '!ping') {
        msg.reply('pong');
    }

    if (msg.body === '!dentro') {
        const nome = msg.author || 'Jogador Desconhecido';
        await adicionarJogador(nome, 'jogador', partidaId, msg);
    }

    if (msg.body === '!fora') {
        const nome = msg.author || 'Jogador Desconhecido';
        await removerJogador(nome, partidaId, msg);
    }

    if (msg.body === '!goleiro') {
        const nome = msg.author || 'Jogador Desconhecido';
        await adicionarJogador(nome, 'goleiro', partidaId, msg);
    }

    if (msg.body === '!lista') {
        msg.reply('Buscando os detalhes da partida...');
        await listarDetalhesPartida(partidaId, msg);
    }
});

// Inicializa o cliente
client.initialize();
