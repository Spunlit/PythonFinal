function selectTicket(ticketType, ticketPrice) {
    // Скрываем все опции
    document.getElementById('ticket-selection').style.display = 'none';

    // Отображаем выбранный билет
    const selectedTicketDiv = document.getElementById('selected-ticket');
    selectedTicketDiv.style.display = 'block';

    // Обновляем данные выбранного билета
    document.getElementById('selected-ticket-name').textContent = `${ticketType} - $${ticketPrice}`;
    document.getElementById('selected-ticket-type').value = ticketType;
}
