const { Client } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');


const client = new Client({
    puppeteer: {
        args: ['--no-sandbox', '--disable-setuid-sandbox'],
    }
});


client.on('ready', () => {
    console.log('FuteBOT is ready!');
});



client.on('qr', qr => {
    qrcode.generate(qr, {small: true});
});


client.on('message', msg => {
    console.log(msg.author);
    console.log(msg.body);
});


client.on('message', msg => {
    if (msg.body == '!ping') {
        msg.reply('pong');
    }
});

client.on('message', msg => {
    if (msg.body == '!dentro') {
        msg.reply('Adiciona jogador');
    }
});

client.on('message', msg => {
    if (msg.body == '!fora') {
        msg.reply('Remove jogador');
    }
});

client.on('message', msg => {
    if (msg.body == '!goleiro') {
        msg.reply('Adiciona goleiro');
    }
});

client.on('message', msg => {
    if (msg.body == '!lista') {
        msg.reply('Lista participantes');
    }
});



client.initialize();
