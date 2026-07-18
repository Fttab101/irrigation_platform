document.addEventListener('DOMContentLoaded', () => {
    const steps = document.querySelectorAll('.wizard-step');
    const dots = document.querySelectorAll('.step-dot');
    const progressBar = document.getElementById('progress-bar');
    const form = document.getElementById('form-parametros');
    const resultsContainer = document.getElementById('results-container');
    const controlFrecuencia = document.getElementById('control-frecuencia');
    
    let currentStep = 1;
    const totalSteps = steps.length;

    // Navigation logic
    const updateWizard = () => {
        steps.forEach((step, index) => {
            if (index + 1 === currentStep) {
                step.classList.add('active');
            } else {
                step.classList.remove('active');
            }
        });

        dots.forEach((dot, index) => {
            if (index + 1 <= currentStep) {
                dot.classList.add('active');
            } else {
                dot.classList.remove('active');
            }
        });

        const progressPercent = ((currentStep - 1) / (totalSteps - 1)) * 100;
        progressBar.style.width = `${progressPercent}%`;
    };

    document.querySelectorAll('.btn-next').forEach(btn => {
        btn.addEventListener('click', () => {
            if (currentStep < totalSteps) {
                currentStep++;
                updateWizard();
            }
        });
    });

    document.querySelectorAll('.btn-prev').forEach(btn => {
        btn.addEventListener('click', () => {
            if (currentStep > 1) {
                currentStep--;
                updateWizard();
            }
        });
    });

    // Form Submission & API Fetching
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Move to step 2 immediately
        currentStep = 2;
        updateWizard();
        
        // Show loading state
        resultsContainer.innerHTML = `
            <div class="loading-state">
                <div class="spinner"></div>
                <p>Procesando algoritmos de riego...</p>
            </div>
        `;

        // Gather data
        const eto = parseFloat(document.getElementById('eto').value);
        const kc = parseFloat(document.getElementById('kc').value);
        const pe = parseFloat(document.getElementById('pe').value);
        const ea = parseFloat(document.getElementById('ea').value);
        const cad = parseFloat(document.getElementById('cad').value);
        const pr = parseFloat(document.getElementById('pr').value);
        const f = parseFloat(document.getElementById('f').value);

        try {
            // Fetch Fase 1: Necesidades
            const resNecesidades = await fetch('/calculos/necesidades', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ eto, kc, pe, ea })
            });
            const dataNecesidades = await resNecesidades.json();

            // Fetch Fase 2: Programación (usando ETc devuelto)
            const resProgramacion = await fetch('/calculos/programacion', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    cad, pr, f, 
                    etc: dataNecesidades.etc 
                })
            });
            const dataProgramacion = await resProgramacion.json();

            // Render Results
            setTimeout(() => {
                resultsContainer.innerHTML = `
                    <div class="result-card">
                        <h3>Evapotranspiración (ETc)</h3>
                        <div class="value">${dataNecesidades.etc} <span style="font-size: 1rem; color: #94a3b8">mm/d</span></div>
                    </div>
                    <div class="result-card">
                        <h3>Dosis Bruta de Riego</h3>
                        <div class="value">${dataNecesidades.db} <span style="font-size: 1rem; color: #94a3b8">mm/d</span></div>
                    </div>
                    <div class="result-card">
                        <h3>Agua Fácil. Disponible</h3>
                        <div class="value">${dataProgramacion.afd} <span style="font-size: 1rem; color: #94a3b8">mm</span></div>
                    </div>
                    <div class="result-card">
                        <h3>Intervalo Máximo</h3>
                        <div class="value">${dataProgramacion.intervalo_maximo_dias} <span style="font-size: 1rem; color: #94a3b8">días</span></div>
                    </div>
                `;

                // Update Control Step dynamically
                controlFrecuencia.innerHTML = `Basado en el intervalo máximo de <strong>${dataProgramacion.intervalo_maximo_dias} días</strong> y el ETc calculado, recomendamos programar riegos cortos diarios o cada 2 días para maximizar la oxigenación radicular, aportando ${dataNecesidades.db} mm diarios.`;

            }, 800); // Fake delay for UX smoothness

        } catch (error) {
            resultsContainer.innerHTML = `
                <div class="alert-box error" style="grid-column: 1/-1; border-left-color: #ef4444; background: rgba(239, 68, 68, 0.1);">
                    <i class="ph ph-warning-circle"></i>
                    <p>Error de conexión con el motor de cálculo. Intenta nuevamente.</p>
                </div>
            `;
            console.error(error);
        }
    });

    // Accordion Logic
    const accordionBtns = document.querySelectorAll('.accordion-btn');
    accordionBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const item = this.parentElement;
            
            // Close others
            document.querySelectorAll('.accordion-item').forEach(otherItem => {
                if(otherItem !== item) {
                    otherItem.classList.remove('active');
                }
            });

            // Toggle current
            item.classList.toggle('active');
        });
    });

    // Initialize
    updateWizard();
});
