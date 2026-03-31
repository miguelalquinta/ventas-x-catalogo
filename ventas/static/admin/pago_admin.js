(function() {
    document.addEventListener('DOMContentLoaded', function() {
        const ventaField = document.getElementById('id_venta');
        if (!ventaField) return;
        
        // Crear contenedor para el resumen
        const resumenDiv = document.createElement('div');
        resumenDiv.id = 'resumen-venta';
        resumenDiv.style.cssText = 'margin-top: 20px; margin-bottom: 20px;';
        
        // Insertar el div después del campo de venta
        ventaField.parentElement.parentElement.insertAdjacentElement('afterend', resumenDiv);
        
        function actualizarResumen() {
            const ventaId = ventaField.value;
            if (!ventaId) {
                resumenDiv.innerHTML = '';
                return;
            }
            
            fetch(`/admin/pagos/pago/api/venta-resumen/${ventaId}/`)
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        resumenDiv.innerHTML = '<p style="color: red;">Error al cargar el resumen</p>';
                        return;
                    }
                    
                    resumenDiv.innerHTML = `
                        <div style="background-color: #e8f4f8; padding: 20px; border-radius: 5px; border-left: 5px solid #0066cc;">
                            <h3 style="margin-top: 0;">Resumen de la Venta</h3>
                            <table style="width: 100%; border-collapse: collapse;">
                                <tr>
                                    <td style="padding: 8px;"><strong>Cliente:</strong></td>
                                    <td style="padding: 8px;">${data.cliente}</td>
                                </tr>
                                <tr style="background-color: #fff;">
                                    <td style="padding: 8px;"><strong>💰 Total Venta:</strong></td>
                                    <td style="padding: 8px; font-size: 18px; color: blue; font-weight: bold;">$${data.total}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px;"><strong>✅ Total Pagado:</strong></td>
                                    <td style="padding: 8px; font-size: 18px; color: green; font-weight: bold;">$${data.pagado}</td>
                                </tr>
                                <tr style="background-color: #fff;">
                                    <td style="padding: 8px;"><strong>⚠️ Saldo Pendiente:</strong></td>
                                    <td style="padding: 8px; font-size: 18px; color: red; font-weight: bold;">$${data.saldo}</td>
                                </tr>
                            </table>
                            <div style="margin-top: 15px;">
                                <p style="margin: 5px 0;"><strong>Porcentaje Pagado: ${data.porcentaje}%</strong></p>
                                <div style="background-color: #ddd; height: 30px; border-radius: 3px; overflow: hidden;">
                                    <div style="background-color: #28a745; height: 100%; width: ${data.porcentaje}%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">
                                        ${data.porcentaje}%
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
                })
                .catch(error => {
                    console.error('Error:', error);
                    resumenDiv.innerHTML = '<p style="color: red;">Error al cargar el resumen</p>';
                });
        }
        
        ventaField.addEventListener('change', actualizarResumen);
        // Actualizar al cargar si ya hay una venta seleccionada
        actualizarResumen();
    });
})();
