(function() {
  'use strict';
  
  document.addEventListener('DOMContentLoaded', function() {
    const ventaSelect = document.getElementById('id_venta');
    
    if (!ventaSelect) return;
    
    function actualizarResumen(ventaId) {
      if (!ventaId) {
        const totalElem = document.getElementById('id_mostrador_total');
        const pagadoElem = document.getElementById('id_mostrador_total_pagado');
        const saldoElem = document.getElementById('id_mostrador_saldo');
        if (totalElem) totalElem.textContent = '-';
        if (pagadoElem) pagadoElem.textContent = '-';
        if (saldoElem) saldoElem.textContent = '-';
        return;
      }
      
      fetch('/admin/pagos/pago/api/venta-resumen/' + ventaId + '/')
        .then(response => response.json())
        .then(data => {
          if (data.error) {
            console.error(data.error);
            return;
          }
          
          const totalElem = document.getElementById('id_mostrador_total');
          const pagadoElem = document.getElementById('id_mostrador_total_pagado');
          const saldoElem = document.getElementById('id_mostrador_saldo');
          
          if (totalElem) totalElem.innerHTML = 'TOTAL: <strong>$' + data.total + '</strong>';
          if (pagadoElem) pagadoElem.innerHTML = '<span style="color: green; font-weight: bold;">PAGADO: $' + data.pagado + '</span>';
          if (saldoElem) saldoElem.innerHTML = '<span style="color: red; font-weight: bold;">PENDIENTE: $' + data.saldo + '</span>';
        })
        .catch(error => console.error('Error:', error));
    }
    
    ventaSelect.addEventListener('change', function() {
      actualizarResumen(this.value);
    });
    
    if (ventaSelect.value) {
      actualizarResumen(ventaSelect.value);
    }
  });
})();
