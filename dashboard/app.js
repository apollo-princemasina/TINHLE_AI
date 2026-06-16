// Environment Configuration
const API_URL = window.ENV?.API_URL || '';

document.addEventListener('DOMContentLoaded', () => {
    const runAssessmentBtn = document.getElementById('run-assessment-btn');
    
    // Set Current Date dynamically
    const today = new Date();
    const options = { month: 'long', day: 'numeric', year: 'numeric' };
    document.getElementById('current-date').textContent = today.toLocaleDateString('en-US', options);

    // Dynamic Baseline Context mapping
    const getMonthContext = (date) => {
        const month = date.toLocaleString('default', { month: 'long' });
        const isDrySeason = [4, 5, 6, 7, 8, 9].includes(date.getMonth()); // May-Oct (approx)
        const avg = isDrySeason ? '2mm' : '85mm';
        const seasonLabel = isDrySeason ? 'Dry Season' : 'Rainy Season';
        return `<i class="ph ph-calendar" aria-hidden="true"></i> ${month} Avg: ${avg} (${seasonLabel})`;
    };
    
    // Set initial baseline
    document.getElementById('baseline-month-info').innerHTML = getMonthContext(today);

    // Helper for Status Badges
    const updateBadge = (elementId, value, type) => {
        const el = document.getElementById(elementId);
        el.textContent = value;
        el.className = `status-badge ${type}`;
    };

    // API Service Layer
    const fetchPrediction = async () => {
        try {
            const response = await fetch(`${API_URL}/predict`);
            if (!response.ok) {
                throw new Error(`API Error: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Failed to fetch prediction:', error);
            throw error;
        }
    };

    // Update UI Elements
    const populateDashboard = (data) => {
        // 1. Location
        document.getElementById('location-text').textContent = data.location;
        document.getElementById('explanation-loc').textContent = data.location;

        // 2. Overall Risk
        const riskPercent = Math.round(data.tinhle_risk * 100);
        document.getElementById('tinhle-risk-percent').textContent = `${riskPercent}%`;
        
        const riskClassEl = document.getElementById('tinhle-risk-class');
        riskClassEl.textContent = data.tinhle_risk_class;
        
        document.getElementById('explanation-class').textContent = `${data.tinhle_risk_class} Risk`;

        // Update Gauge Math & Color
        const gauge = document.getElementById('risk-gauge-circle');
        const circumference = 251.2; 
        const offset = circumference - (riskPercent / 100) * circumference;
        gauge.style.strokeDashoffset = offset;
        
        let gaugeColor = 'var(--green)';
        let badgeType = 'stable';
        
        if(data.tinhle_risk_class === 'HIGH') {
            gaugeColor = 'var(--orange)';
            badgeType = 'critical';
        } else if (data.tinhle_risk_class === 'MODERATE') {
            gaugeColor = 'var(--yellow)';
            badgeType = 'moderate';
        }
        
        gauge.style.stroke = gaugeColor;
        document.getElementById('explanation-class').style.color = gaugeColor;
        riskClassEl.className = `label badge-status status-badge ${badgeType}`;

        // Calculate reused metrics
        const droughtProbPercent = Math.round(data.drought_probability * 100);
        const commRiskPercent = Math.round(data.community_risk * 100);

        // 3. Key Drivers summary
        const droughtBadge = data.drought_class === 'HIGH' ? 'critical' : data.drought_class === 'MODERATE' ? 'moderate' : 'stable';
        updateBadge('drought-driver', `${droughtProbPercent}% (${data.drought_class})`, droughtBadge);
        
        const envBadge = data.environmental_label === 'CRITICAL' ? 'severe' : data.environmental_label === 'WARNING' ? 'moderate' : 'stable';
        updateBadge('env-driver', `${data.environmental_score.toFixed(2)} (${data.environmental_label})`, envBadge);
        
        const commBadge = commRiskPercent > 60 ? 'critical' : commRiskPercent > 30 ? 'moderate' : 'stable';
        updateBadge('community-driver', `${commRiskPercent}% Risk`, commBadge);

        // 4. Rainfall Forecast
        document.getElementById('val-rainfall').textContent = data.predicted_rainfall.toFixed(1);

        // 5. Drought Model
        document.getElementById('val-drought-prob').textContent = `${droughtProbPercent}%`;
        document.getElementById('bar-drought-prob').style.width = `${droughtProbPercent}%`;
        
        const valDroughtClass = document.getElementById('val-drought-class');
        valDroughtClass.textContent = data.drought_class;
        
        const barDroughtClass = document.getElementById('bar-drought-class');
        if (data.drought_class === 'HIGH') {
            valDroughtClass.className = 'status-text font-bold text-orange';
            barDroughtClass.className = 'fill bg-orange';
            barDroughtClass.style.width = '100%';
        } else if (data.drought_class === 'MODERATE') {
            valDroughtClass.className = 'status-text font-bold text-yellow';
            barDroughtClass.className = 'fill bg-yellow';
            barDroughtClass.style.width = '60%';
        } else {
            valDroughtClass.className = 'status-text font-bold text-green';
            barDroughtClass.className = 'fill bg-green';
            barDroughtClass.style.width = '20%';
        }

        // 6. Environmental Intel
        document.getElementById('val-env-score').textContent = data.environmental_score.toFixed(2);
        
        const valEnvLabel = document.getElementById('val-env-label');
        valEnvLabel.textContent = data.environmental_label;
        valEnvLabel.className = `status-text ${data.environmental_label === 'CRITICAL' ? 'text-red' : 'text-green'}`;

        // 7. Community Intel
        document.getElementById('val-reports').textContent = data.reports_used;
        document.getElementById('val-community-risk').textContent = `${commRiskPercent}%`;
        
        const statusText = commRiskPercent > 60 ? 'CRITICAL' : commRiskPercent > 30 ? 'ELEVATED' : 'STABLE';
        updateBadge('val-community-status', statusText, commBadge + " small");

        // Update Recommendation based on class
        const recText = data.tinhle_risk_class === 'HIGH' 
            ? 'Prioritize drought-resistant crop varieties and implement immediate water-harvesting interventions.'
            : 'Maintain standard monitoring and preserve current soil moisture levels.';
        document.getElementById('ai-recommendation').textContent = recText;
    };

    // Run Assessment Button Logic
    runAssessmentBtn.addEventListener('click', async () => {
        if(runAssessmentBtn.classList.contains('loading')) return;

        // Set Loading state
        const originalContent = runAssessmentBtn.innerHTML;
        runAssessmentBtn.setAttribute('aria-busy', 'true');
        runAssessmentBtn.classList.add('loading');
        runAssessmentBtn.innerHTML = '<i class="ph ph-spinner-gap spin" aria-hidden="true"></i> Running Assessment...';

        try {
            const data = await fetchPrediction();
            populateDashboard(data);

            runAssessmentBtn.classList.remove('loading');
            runAssessmentBtn.innerHTML = '<i class="ph ph-check-circle" aria-hidden="true"></i> Assessment Complete';
            runAssessmentBtn.style.background = 'var(--green)';
            runAssessmentBtn.style.color = 'white';
        } catch (error) {
            runAssessmentBtn.classList.remove('loading');
            runAssessmentBtn.innerHTML = '<i class="ph ph-warning-circle" aria-hidden="true"></i> Assessment Failed';
            runAssessmentBtn.style.background = 'var(--red)';
            runAssessmentBtn.style.color = 'white';
            alert('Failed to connect to the AI model API. Is the FastAPI server running?');
        } finally {
            runAssessmentBtn.removeAttribute('aria-busy');
            setTimeout(() => {
                runAssessmentBtn.innerHTML = originalContent;
                runAssessmentBtn.style.background = '';
                runAssessmentBtn.style.color = '';
            }, 3000);
        }
    });

    // Share Report Button Logic
    const shareReportBtn = document.getElementById('share-report-btn');
    shareReportBtn.addEventListener('click', async () => {
        const originalContent = shareReportBtn.innerHTML;
        shareReportBtn.innerHTML = '<i class="ph ph-spinner-gap spin"></i> Sending...';
        
        try {
            const response = await fetch(`${API_URL}/send-report`);
            if (!response.ok) throw new Error();
            
            shareReportBtn.innerHTML = '<i class="ph ph-check-circle"></i> Sent!';
            shareReportBtn.style.background = 'var(--green)';
        } catch (error) {
            shareReportBtn.innerHTML = '<i class="ph ph-warning-circle"></i> Failed';
            shareReportBtn.style.background = 'var(--red)';
        } finally {
            setTimeout(() => {
                shareReportBtn.innerHTML = originalContent;
                shareReportBtn.style.background = '';
            }, 3000);
        }
    });
});
