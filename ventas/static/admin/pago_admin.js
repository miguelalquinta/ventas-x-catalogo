(function() {
  'use strict';
  
  document.addEventListener('DOMContentLoaded', function() {
    const ventaSelect = document.getElementById('id_venta');
    
    if (!ventaSelect) {
      console.log('No venta select found');
      return;
    }
    
    console.log('Pago admin JS loaded');
    
    function actualizarResumen(ventaId) {
      console.log('Updating resumen for venta ID:', ventaId);
      
      if (!ventaId) {
        document.getElementById('resumen-cliente').textContent = 'Selecciona una venta';
        document.getElementById('resumen-total').textContent = '-';
        document.getElementById('resumen-pagado').textContent = '-';
        document.getElementById('resumen-saldo').textContent = '-';
        document.getElementById('resumen-porcentaje').textContent = '0';
        document.getElementById('resumen-barra').style.width = '0%';
        return;
      }
      
      const apiUrl = '/admin/pagos/pago/api/venta-resumen/' + ventaId + '/';
      console.log('Fetching from:', apiUrl);
      
      fetch(apiUrl)
        .then(response => {
          console.log('Response status:', response.status);
          return response.json();
        })
        .then(data => {
          console.log('Data received:', data);
          
          if (data.error) {
            console.error('Error:', data.error);
            return;
          }
          
          document.getElementById('resumen-cliente').textContent = data.cliente;
          document.getElementById('resumen-total').textContent = '$' + data.total;
          document.getElementById('resumen-pagado').textContent = '$' + data.pagado;
          document.getElementById('resumen-saldo').textContent = '$' + data.saldo;
          document.getElementById('resumen-porcentaje').textContent = data.porcentaje;
          document.getElementById('resumen-barra').style.width = data.porcentaje + '%';
        })
        .catch(error => {
          console.error('Fetch error:', error);
        });
    }
    
    ventaSelect.addEventListener('change', function() {
      console.log('Venta changed to:', this.value);
      actualizarResumen(this.value);
    });
    
    // Si ya hay una venta seleccionada, actualizar resumen
    if (ventaSelect.value) {
      console.log('Initial venta value:', ventaSelect.value);
      actualizarResumen(ventaSelect.value);
    }
  });
})();
