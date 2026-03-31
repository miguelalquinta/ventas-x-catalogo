cd /home/malquinta/ventas-x-catalogo
mkdir -p ventas/static/admin
cat > ventas/static/admin/pago_admin.js << 'EOF'
(function() {
  'use strict';
  
  document.addEventListener('DOMContentLoaded', function() {
    const ventaSelect = document.getElementById('id_venta');
    
    if (!ventaSelect) return;
    
    function actualizarResumen(ventaId) {
      if (!ventaId) {
        document.getElementById('id_mostrador_total').textContent = '-';
        document.getElementById('id_mostrador_total_pagado').textContent = '-';
        document.getElementById('id_mostrador_saldo').textContent = '-';
        return;
      }
      
      fetch(`/admin/pagos/pago/api/venta-resumen/${ventaId}/`)
        .then(response => response.json())
        .then(data => {
          if (data.error) {
            console.error(data.error);
            return;
          }
          
          const totalElem = document.getElementById('id_mostrador_total');
          const pagadoElem = document.getElementById('id_mostrador_total_pagado');
          const saldoElem = document.getElementById('id_mostrador_saldo');
          
          if (totalElem) totalElem.innerHTML = `💰 <strong>$${data.total}</strong>`;
          if (pagadoElem) pagadoElem.innerHTML = `<span style="color: green; font-weight: bold;">✅ $${data.pagado}</span>`;
          if (saldoElem) saldoElem.innerHTML = `<span style="color: ${data.saldo === '0' ? 'green' : '#ff6b6b'}; font-weight: bold;">⚠️ $${data.saldo}</span>`;
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
