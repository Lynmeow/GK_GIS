/* =============================================
   MAP.JS — Leaflet · Light Theme + GEE Layers
   ============================================= */

document.addEventListener('DOMContentLoaded', function () {

    const map = L.map('main-map', {
        center: [10.8231, 106.6297],
        zoom: 11,
        zoomControl: true,
        attributionControl: true,
    });

    window._leafletMap = map;

    const baseLayers = {
        light: L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
            attribution: '© OpenStreetMap © CARTO', subdomains: 'abcd', maxZoom: 19,
        }),
        satellite: L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
            attribution: '© Esri', maxZoom: 19,
        }),
    };

    baseLayers.light.addTo(map);

    // ── Color helpers ──
    function pm25Color(pm25) {
        if (pm25 <= 12) return { fill: '#06D6A0', border: '#05a07a', text: '#fff' };
        if (pm25 <= 25) return { fill: '#FFD60A', border: '#d4a800', text: '#333' };
        if (pm25 <= 50) return { fill: '#FF9A3C', border: '#d4720a', text: '#fff' };
        return                 { fill: '#EF233C', border: '#b01528', text: '#fff' };
    }

    function pm25Label(pm25) {
        if (pm25 <= 12) return 'Tốt';
        if (pm25 <= 25) return 'Trung bình';
        if (pm25 <= 50) return 'Kém';
        return 'Xấu';
    }

    function hasValue(v) { return v !== undefined && v !== null; }
    function fmtValue(v, suffix = '') { return hasValue(v) ? `${v}${suffix}` : '--'; }

    // ── Tab helpers ──
    function lockTabs() {
        document.querySelectorAll('.map-layer-tab').forEach(btn => {
            btn.disabled = true;
            btn.style.pointerEvents = 'none';
            btn.style.cursor = 'not-allowed';
        });
    }

    function unlockTabs(activeLayer) {
        document.querySelectorAll('.map-layer-tab').forEach(btn => {
            const isActive = btn.dataset.layer === activeLayer;
            btn.disabled = false;
            btn.classList.toggle('active', isActive);
            btn.style.opacity       = isActive ? '1' : '0.45';
            btn.style.pointerEvents = 'auto';
            btn.style.cursor        = 'pointer';
        });
        const enableAll = (activeLayer === 'satellite' || activeLayer === 'risk');
        document.querySelectorAll('.sidebar-section .layer-item').forEach(item => {
            const input = item.querySelector('input[type="checkbox"]');
            if (!input) return;
            const match = (input.getAttribute('onchange') || '').match(/toggleLayer\('(\w+)'/);
            if (!match) return;
            const isRelevant = enableAll || (match[1] === activeLayer);
            item.style.opacity       = isRelevant ? '1'    : '0.35';
            item.style.pointerEvents = isRelevant ? 'auto' : 'none';
            const opacityRow = item.nextElementSibling;
            if (opacityRow && opacityRow.classList.contains('layer-opacity')) {
                opacityRow.style.opacity       = isRelevant ? '1'    : '0.35';
                opacityRow.style.pointerEvents = isRelevant ? 'auto' : 'none';
            }
        });
    }

    // ── District markers ──
    let districtMarkers = [];
    let currentMapMode  = 'satellite';

    async function loadDistrictMarkers() {
        if (currentMapMode !== 'satellite' && currentMapMode !== 'air') return;
        try {
            const res  = await fetch('/api/districts/');
            const json = await res.json();
            if (!json.success) throw new Error('API failed');
            districtMarkers.forEach(m => map.removeLayer(m));
            districtMarkers = [];
            json.districts.forEach(d => {
                const c    = pm25Color(d.pm25);
                const icon = L.divIcon({
                    html: `<div style="width:40px;height:40px;background:${c.fill};border:2.5px solid ${c.border};border-radius:50%;display:flex;align-items:center;justify-content:center;font-family:'DM Sans',sans-serif;font-size:11px;font-weight:700;color:${c.text};box-shadow:0 3px 12px rgba(0,0,0,0.15),0 0 0 4px ${c.fill}33;cursor:pointer;">${d.pm25}</div>`,
                    className: '', iconSize: [40,40], iconAnchor: [20,20],
                });
                const marker = L.marker([d.lat, d.lng], { icon }).addTo(map)
                    .bindTooltip(`<b>${d.name}</b><br>PM2.5: ${d.pm25} µg/m³ — ${pm25Label(d.pm25)}<br>AQI: ${d.aqi} | NO₂: ${d.no2} µg/m³`, { direction:'top', offset:[0,-22], className:'leaflet-light-tooltip' });
                marker.on('click', function(e) {
                    showPopup({ name:d.name, lat:d.lat, lng:d.lng, aqi:d.aqi, pm25:d.pm25, no2:d.no2, ndvi:hasValue(d.ndvi)?d.ndvi:'--', lst:hasValue(d.lst)?d.lst:'--' }, e.originalEvent);
                });
                districtMarkers.push(marker);
            });
        } catch(e) { console.warn('District API error, dùng mock data:', e); loadMockMarkers(); }
    }

    function loadMockMarkers() {
        const mockData = [
            { name:'Quận 1',     lat:10.7769, lng:106.7009, aqi:95,  pm25:42,  no2:12, ndvi:0.18, lst:38.5 },
            { name:'Quận 3',     lat:10.7838, lng:106.6861, aqi:88,  pm25:38,  no2:10, ndvi:0.22, lst:37.8 },
            { name:'Quận 7',     lat:10.7340, lng:106.7218, aqi:72,  pm25:30,  no2:8,  ndvi:0.35, lst:36.2 },
            { name:'Quận 12',    lat:10.8627, lng:106.6564, aqi:110, pm25:52,  no2:15, ndvi:0.28, lst:40.1 },
            { name:'Bình Chánh', lat:10.6746, lng:106.5956, aqi:142, pm25:58,  no2:18, ndvi:0.31, lst:39.8 },
            { name:'Hóc Môn',    lat:10.8914, lng:106.5929, aqi:128, pm25:55,  no2:16, ndvi:0.38, lst:38.9 },
            { name:'Thủ Đức',    lat:10.8600, lng:106.7515, aqi:71,  pm25:28,  no2:7,  ndvi:0.42, lst:35.8 },
            { name:'Bình Thạnh', lat:10.8119, lng:106.7106, aqi:87,  pm25:36,  no2:10, ndvi:0.25, lst:37.5 },
            { name:'Gò Vấp',     lat:10.8383, lng:106.6658, aqi:102, pm25:46,  no2:13, ndvi:0.24, lst:39.0 },
            { name:'Nhà Bè',     lat:10.6910, lng:106.7381, aqi:60,  pm25:22,  no2:6,  ndvi:0.52, lst:34.5 },
            { name:'Cần Giờ',    lat:10.4110, lng:106.9529, aqi:42,  pm25:14,  no2:4,  ndvi:0.71, lst:32.1 },
            { name:'Củ Chi',     lat:11.0019, lng:106.4942, aqi:55,  pm25:20,  no2:5,  ndvi:0.58, lst:33.8 },
        ];
        districtMarkers.forEach(m => map.removeLayer(m));
        districtMarkers = [];
        mockData.forEach(d => {
            const c = pm25Color(d.pm25);
            const icon = L.divIcon({
                html: `<div style="width:40px;height:40px;background:${c.fill};border:2.5px solid ${c.border};border-radius:50%;display:flex;align-items:center;justify-content:center;font-family:'DM Sans',sans-serif;font-size:11px;font-weight:700;color:${c.text};box-shadow:0 3px 12px rgba(0,0,0,0.15),0 0 0 4px ${c.fill}33;cursor:pointer;">${d.pm25}</div>`,
                className:'', iconSize:[40,40], iconAnchor:[20,20],
            });
            const marker = L.marker([d.lat,d.lng],{icon}).addTo(map)
                .bindTooltip(`<b>${d.name}</b><br>PM2.5: ${d.pm25} µg/m³ | AQI: ${d.aqi}`, {direction:'top',offset:[0,-22],className:'leaflet-light-tooltip'});
            marker.on('click', function(e) { showPopup(d, e.originalEvent); });
            districtMarkers.push(marker);
        });
    }

    // ── Trạm quan trắc ──
    const stations = [
        { name:'Trạm KK Bình Chánh',   lat:10.6800, lng:106.6100, type:'air',     icon:'💨' },
        { name:'Trạm KK Thủ Đức',      lat:10.8550, lng:106.7600, type:'air',     icon:'💨' },
        { name:'Trạm KK Hóc Môn',      lat:10.8800, lng:106.5950, type:'air',     icon:'💨' },
        { name:'Trạm Nước Sông SG',     lat:10.7700, lng:106.7100, type:'water',   icon:'💧' },
        { name:'Trạm KT Tân Sơn Nhất', lat:10.8122, lng:106.6560, type:'weather', icon:'🌤' },
    ];
    const stationColors = { air:'#00B4D8', water:'#0077B6', weather:'#06D6A0' };
    let stationMarkers = [];
    stations.forEach(s => {
        const color = stationColors[s.type];
        const icon  = L.divIcon({
            html:`<div style="width:30px;height:30px;background:#fff;border:2px solid ${color};border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:13px;box-shadow:0 2px 8px ${color}44;">${s.icon}</div>`,
            className:'', iconSize:[30,30], iconAnchor:[15,15],
        });
        stationMarkers.push(L.marker([s.lat,s.lng],{icon}).addTo(map).bindTooltip(`<b>${s.name}</b>`,{direction:'top',className:'leaflet-light-tooltip'}));
    });

    window.toggleStations = function(show) { stationMarkers.forEach(m => show ? m.addTo(map) : m.remove()); };
    window.toggleLayer    = function(layerName, show) { if (activeGeeLayer && currentGeeLayer === layerName) { show ? activeGeeLayer.addTo(map) : map.removeLayer(activeGeeLayer); } };
    window.setLayerOpacity = function(layerName, value) { if (activeGeeLayer && currentGeeLayer === layerName) activeGeeLayer.setOpacity(value/100); };

    // ── GEE Layers ──
    let activeGeeLayer = null, currentGeeLayer = null;

    async function loadGeeLayer(layerName, callback) {
        if (currentGeeLayer === layerName && activeGeeLayer) {
            map.removeLayer(activeGeeLayer); activeGeeLayer = null; currentGeeLayer = null;
            const panel = document.getElementById('geeDataPanel');
            if (panel) panel.style.display = 'none';
            if (callback) callback(); return;
        }
        if (activeGeeLayer) { map.removeLayer(activeGeeLayer); activeGeeLayer = null; currentGeeLayer = null; }
        if (!['air','lst','water','ndvi','flood'].includes(layerName)) { if (callback) callback(); return; }
        try {
            const json = await (await fetch(`/api/gee/tile/?layer=${layerName}`)).json();
            if (!json.success) { console.error('GEE error:', json.error); if (callback) callback(); return; }
            const tileLayer = L.tileLayer(json.tile_url, { opacity:0.75, maxZoom:13 });
            tileLayer.addTo(map); activeGeeLayer = tileLayer; currentGeeLayer = layerName;
            updateDataPanel(layerName, json.data);
            const sourceMap = { air:'Sentinel-5P · NO₂/CO', lst:'Landsat 8 · LST/NDVI', water:'Sentinel-2 · NDWI', ndvi:'Sentinel-2 · NDVI/EVI', flood:'Sentinel-1 SAR · VV' };
            const statusEl = document.getElementById('statusLayer');
            if (statusEl) statusEl.textContent = `Nguồn: GEE · ${sourceMap[layerName]}`;
            if (callback) callback();
        } catch(e) { console.error('Load GEE failed:', e); if (callback) callback(); }
    }

    function updateDataPanel(layer, data) {
        const panel = document.getElementById('geeDataPanel'), title = document.getElementById('geeDataTitle'), content = document.getElementById('geeDataContent');
        if (!panel) return;
        const sd = data || {};
        const titles = { air:'🌫 Không khí (Sentinel-5P)', lst:'🌡 Nhiệt bề mặt (Landsat 8)', water:'💧 Chất lượng nước (Sentinel-2)', ndvi:'🌿 Thảm thực vật (Sentinel-2)', flood:'🌊 Ngập úng (Sentinel-1)' };
        const labels = { air:[['NO₂',sd.no2,'µmol/m²'],['CO',sd.co,'mol/m²']], lst:[['LST',sd.lst,'°C'],['NDVI',sd.ndvi,''],['NDBI',sd.ndbi,'']], water:[['NDWI',sd.ndwi,''],['MNDWI',sd.mndwi,'']], ndvi:[['NDVI',sd.ndvi,''],['EVI',sd.evi,'']], flood:[['VV Backscatter',sd.vv_backscatter,'dB']] };
        title.textContent = titles[layer] || 'Dữ liệu GEE';
        content.innerHTML = (labels[layer]||[]).map(([l,v,u]) => `<div style="display:flex;justify-content:space-between;align-items:center;padding:6px 0;border-bottom:1px solid rgba(0,180,216,0.08);"><span style="font-size:12px;color:#5A8DB8">${l}</span><span style="font-size:13px;font-weight:700;color:#023E8A">${hasValue(v)?v:'—'}<span style="font-size:10px;color:#90B8D4">${u}</span></span></div>`).join('')
            + (sd.start_date ? `<div style="font-size:10px;color:#90B8D4;margin-top:6px;text-align:right">${sd.start_date} → ${sd.end_date}</div>` : '');
        panel.style.display = 'block';
    }

    // ── mapInstance ──
    window.mapInstance = {
        setActiveLayer: function(layer, callback) {
            currentMapMode = layer; lockTabs();
            if (!['air','lst','water','ndvi','flood'].includes(layer)) {
                if (activeGeeLayer) { map.removeLayer(activeGeeLayer); activeGeeLayer = null; currentGeeLayer = null; }
                const panel = document.getElementById('geeDataPanel');
                if (panel) panel.style.display = 'none';
            }
            Object.values(baseLayers).forEach(l => map.removeLayer(l));
            const done = () => { unlockTabs(layer); if (callback) callback(); };
            if (layer === 'satellite') {
                baseLayers.satellite.addTo(map); reloadMarkersForLayer('satellite');
                const el = document.getElementById('statusLayer'); if (el) el.textContent = 'Bản đồ vệ tinh · Esri World Imagery';
                done();
            } else if (layer === 'risk') {
                baseLayers.light.addTo(map); reloadMarkersForLayer('risk');
                const el = document.getElementById('statusLayer'); if (el) el.textContent = 'Bản đồ rủi ro · AQI + LST + NDVI';
                done();
            } else {
                baseLayers.light.addTo(map); reloadMarkersForLayer(layer); loadGeeLayer(layer, done);
            }
        }
    };

    function reloadMarkersForLayer(layer) {
        if (layer === 'risk') {
            districtMarkers.forEach(m => m.remove()); districtMarkers = [];
            fetch('/api/risk/').then(r=>r.json()).then(json => {
                if (!json.success || !Array.isArray(json.districts)) return;
                json.districts.forEach(d => {
                    const fill=d.risk_color||'#90B8D4', score=d.risk_score||'--';
                    const icon=L.divIcon({html:`<div style="width:44px;height:44px;background:${fill};border:2.5px solid ${fill};border-radius:50%;display:flex;flex-direction:column;align-items:center;justify-content:center;font-family:'DM Sans',sans-serif;color:#fff;box-shadow:0 3px 12px rgba(0,0,0,0.2);cursor:pointer;text-align:center;line-height:1.2;"><span style="font-size:9px;font-weight:700;">${score}</span><span style="font-size:7px;opacity:0.85">${d.risk_label}</span></div>`,className:'',iconSize:[44,44],iconAnchor:[22,22]});
                    const marker=L.marker([d.lat,d.lng],{icon}).addTo(map).bindTooltip(`<b>${d.name}</b><br>Rủi ro: ${d.risk_label} (${score}/100)<br>AQI: ${d.aqi} | LST: ${d.lst}°C | NDVI: ${d.ndvi}`,{direction:'top',offset:[0,-24],className:'leaflet-light-tooltip'});
                    marker.on('click',function(e){showRiskPopup(d,e.originalEvent);}); districtMarkers.push(marker);
                });
            }).catch(()=>{});
            return;
        }
        if (layer === 'flood') {
            districtMarkers.forEach(m => m.remove()); districtMarkers = [];
            fetch('/api/flood/districts/?days=30').then(r=>r.json()).then(json=>{
                if (!json.success||!Array.isArray(json.districts)) return;
                json.districts.forEach(d=>{
                    const fill={high:'#EF233C',medium:'#FF9A3C',low:'#06D6A0'}[d.risk]||'#90B8D4';
                    const icon=L.divIcon({html:`<div style="width:40px;height:40px;background:${fill};border:2.5px solid ${fill};border-radius:50%;display:flex;align-items:center;justify-content:center;font-family:'DM Sans',sans-serif;font-size:9px;font-weight:700;color:#fff;box-shadow:0 3px 12px rgba(0,0,0,0.15);cursor:pointer;text-align:center;line-height:1.2;">${d.vv}<br>dB</div>`,className:'',iconSize:[40,40],iconAnchor:[20,20]});
                    const marker=L.marker([d.lat,d.lng],{icon}).addTo(map).bindTooltip(`<b>${d.name}</b><br>VV: ${d.vv} dB<br>Nguy cơ: ${d.risk_label}`,{direction:'top',offset:[0,-22],className:'leaflet-light-tooltip'});
                    marker.on('click',function(e){showPopup(d,e.originalEvent);}); districtMarkers.push(marker);
                });
            }).catch(()=>{});
            return;
        }
        if (layer === 'water') {
            districtMarkers.forEach(m => m.remove()); districtMarkers = [];
            [{name:'Sông Sài Gòn',lat:10.7800,lng:106.7050,ndwi:0.42},{name:'Sông Đồng Nai',lat:10.8500,lng:106.7800,ndwi:0.38},{name:'Kênh Tẻ',lat:10.7450,lng:106.7100,ndwi:0.31},{name:'Kênh Đôi',lat:10.7300,lng:106.6600,ndwi:0.28},{name:'Sông Nhà Bè',lat:10.6800,lng:106.7300,ndwi:0.45},{name:'Sông Lòng Tàu',lat:10.5500,lng:106.8200,ndwi:0.50},{name:'Kênh Nhiêu Lộc',lat:10.7950,lng:106.6900,ndwi:0.18},{name:'Rạch Bến Cát',lat:10.8200,lng:106.6700,ndwi:0.22}].forEach(d=>{
                const t=Math.max(0,Math.min(1,(d.ndwi+0.2)/0.8));
                const fill=`rgb(${Math.round(Math.max(0,255-t*255))},50,${Math.round(Math.min(255,t*255))})`;
                const quality=d.ndwi>0.3?'💧 Tốt':d.ndwi>0.1?'⚠ Trung bình':'🔴 Ô nhiễm';
                const icon=L.divIcon({html:`<div style="width:40px;height:40px;background:${fill};border:2.5px solid ${fill};border-radius:50%;display:flex;align-items:center;justify-content:center;font-family:'DM Sans',sans-serif;font-size:9px;font-weight:700;color:#fff;box-shadow:0 3px 12px rgba(0,0,0,0.15);cursor:pointer;text-align:center;line-height:1.2;">${d.ndwi}</div>`,className:'',iconSize:[40,40],iconAnchor:[20,20]});
                districtMarkers.push(L.marker([d.lat,d.lng],{icon}).addTo(map).bindTooltip(`<b>${d.name}</b><br>NDWI: ${d.ndwi}<br>${quality}`,{direction:'top',offset:[0,-22],className:'leaflet-light-tooltip'}));
            });
            return;
        }
        districtMarkers.forEach(m => map.removeLayer(m)); districtMarkers = [];
        fetch('/api/districts/').then(r=>r.json()).then(json=>{
            if (!json.success||!Array.isArray(json.districts)) throw new Error();
            json.districts.forEach(d=>buildMarkerForLayer(d,layer));
        }).catch(()=>{
            [{name:'Quận 1',lat:10.7769,lng:106.7009,aqi:95,pm25:42,no2:12,ndvi:0.18,lst:38.5},{name:'Quận 3',lat:10.7838,lng:106.6861,aqi:88,pm25:38,no2:10,ndvi:0.22,lst:37.8},{name:'Quận 7',lat:10.7340,lng:106.7218,aqi:72,pm25:30,no2:8,ndvi:0.35,lst:36.2},{name:'Quận 12',lat:10.8627,lng:106.6564,aqi:110,pm25:52,no2:15,ndvi:0.28,lst:40.1},{name:'Bình Chánh',lat:10.6746,lng:106.5956,aqi:142,pm25:58,no2:18,ndvi:0.31,lst:39.8},{name:'Hóc Môn',lat:10.8914,lng:106.5929,aqi:128,pm25:55,no2:16,ndvi:0.38,lst:38.9},{name:'Thủ Đức',lat:10.8600,lng:106.7515,aqi:71,pm25:28,no2:7,ndvi:0.42,lst:35.8},{name:'Bình Thạnh',lat:10.8119,lng:106.7106,aqi:87,pm25:36,no2:10,ndvi:0.25,lst:37.5},{name:'Gò Vấp',lat:10.8383,lng:106.6658,aqi:102,pm25:46,no2:13,ndvi:0.24,lst:39.0},{name:'Nhà Bè',lat:10.6910,lng:106.7381,aqi:60,pm25:22,no2:6,ndvi:0.52,lst:34.5},{name:'Cần Giờ',lat:10.4110,lng:106.9529,aqi:42,pm25:14,no2:4,ndvi:0.71,lst:32.1},{name:'Củ Chi',lat:11.0019,lng:106.4942,aqi:55,pm25:20,no2:5,ndvi:0.58,lst:33.8}]
            .forEach(d=>buildMarkerForLayer(d,layer));
        });
    }

    function buildMarkerForLayer(d, layer) {
        let value, unit, label, c;
        if (layer==='lst') { value=d.lst; unit='°C'; label='LST'; const t=Math.max(0,Math.min(1,(d.lst-30)/15)); c={fill:`rgb(${Math.round(Math.min(255,t*510))},${Math.round(Math.max(0,255-t*510))},50)`,text:'#fff'}; c.border=c.fill; }
        else if (layer==='ndvi') { value=d.ndvi; unit=''; label='NDVI'; const t=Math.max(0,Math.min(1,(d.ndvi+0.2)/1.0)); c={fill:`rgb(${Math.round(Math.max(0,255-t*255))},${Math.round(Math.min(255,t*255))},50)`,text:'#fff'}; c.border=c.fill; }
        else { value=d.pm25; unit='µg/m³'; label='PM2.5'; c=pm25Color(d.pm25); }
        const displayVal=hasValue(value)?value:'--';
        const icon=L.divIcon({html:`<div style="width:40px;height:40px;background:${c.fill};border:2.5px solid ${c.border};border-radius:50%;display:flex;align-items:center;justify-content:center;font-family:'DM Sans',sans-serif;font-size:10px;font-weight:700;color:${c.text};box-shadow:0 3px 12px rgba(0,0,0,0.15),0 0 0 4px ${c.fill}33;cursor:pointer;">${displayVal}</div>`,className:'',iconSize:[40,40],iconAnchor:[20,20]});
        const marker=L.marker([d.lat,d.lng],{icon}).addTo(map).bindTooltip(`<b>${d.name}</b><br>${label}: ${displayVal} ${unit}`,{direction:'top',offset:[0,-22],className:'leaflet-light-tooltip'});
        marker.on('click',function(e){showPopup(d,e.originalEvent);}); districtMarkers.push(marker);
    }

    // ── Popups ──
    function showRiskPopup(d, event) {
        const popup=document.getElementById('mapPopup'); if (!popup) return;
        const causes=(d.causes||[]).map(c=>`<div style="font-size:11px;color:#5A8DB8;padding:2px 0">⚠ ${c.msg}</div>`).join('');
        const recs=(d.recommendations||[]).map(r=>`<div style="font-size:11px;color:#023E8A;padding:2px 0">${r}</div>`).join('');
        document.getElementById('popupDistrict').textContent=d.name||'--';
        document.getElementById('popupAqi').textContent=fmtValue(d.aqi);
        document.getElementById('popupPm25').textContent=fmtValue(d.lst,'°C');
        document.getElementById('popupNdvi').textContent=fmtValue(d.ndvi);
        document.getElementById('popupLst').textContent=hasValue(d.risk_score)?`${d.risk_score}/100`:'--';
        const labs=popup.querySelectorAll('.popup-stat-label');
        if(labs[0])labs[0].textContent='AQI'; if(labs[1])labs[1].textContent='LST'; if(labs[2])labs[2].textContent='NDVI'; if(labs[3])labs[3].textContent='Rủi ro';
        document.getElementById('popupAqi').className='popup-stat-value '+(d.aqi>100?'bad':d.aqi>70?'warn':'good');
        document.getElementById('popupTime').innerHTML=`<div style="font-size:11px;font-weight:700;color:${d.risk_color||'#023E8A'}">${d.risk_label||'--'}</div><div style="margin-top:6px">${causes||'<div style="font-size:11px;color:#5A8DB8">Không có dữ liệu nguyên nhân.</div>'}</div><div style="margin-top:6px;border-top:1px solid rgba(0,180,216,0.1);padding-top:6px"><div style="font-size:10px;font-weight:700;color:#023E8A;margin-bottom:4px">💡 Đề xuất:</div>${recs||'<div style="font-size:11px;color:#5A8DB8">Chưa có khuyến nghị.</div>'}</div>`;
        positionPopup(popup,event,260);
    }

    function showPopup(d, event) {
        const popup=document.getElementById('mapPopup'); if (!popup) return;
        document.getElementById('popupDistrict').textContent=d.name||'--';
        document.getElementById('popupAqi').textContent=fmtValue(d.aqi);
        document.getElementById('popupPm25').textContent=fmtValue(d.pm25,' µg/m³');
        document.getElementById('popupNdvi').textContent=fmtValue(d.ndvi);
        document.getElementById('popupLst').textContent=fmtValue(d.lst,'°C');
        const labs=popup.querySelectorAll('.popup-stat-label');
        if(labs[0])labs[0].textContent='AQI'; if(labs[1])labs[1].textContent='PM2.5'; if(labs[2])labs[2].textContent='NDVI'; if(labs[3])labs[3].textContent='LST';
        document.getElementById('popupAqi').className='popup-stat-value '+(d.aqi>100?'bad':d.aqi>70?'warn':'good');
        const now=new Date();
        document.getElementById('popupTime').textContent=`Cập nhật: ${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}`;
        positionPopup(popup,event,250);
    }

    function positionPopup(popup, event, width) {
        const rect=document.getElementById('main-map').getBoundingClientRect();
        let x=event.clientX-rect.left+16, y=event.clientY-rect.top-20;
        if (x+width>rect.width) x=event.clientX-rect.left-width;
        popup.style.left=x+'px'; popup.style.top=y+'px'; popup.classList.add('show');
    }

    window.closePopup = function() { const p=document.getElementById('mapPopup'); if(p) p.classList.remove('show'); };

    map.on('mousemove', function(e) { const el=document.getElementById('statusCoord'); if(el) el.textContent=`${e.latlng.lat.toFixed(4)}°N, ${e.latlng.lng.toFixed(4)}°E`; });
    map.on('zoomend',  function()  { const el=document.getElementById('statusZoom');  if(el) el.textContent=map.getZoom(); });

    const style=document.createElement('style');
    style.textContent=`.leaflet-light-tooltip{background:#fff!important;border:1.5px solid rgba(0,180,216,0.25)!important;color:#03045E!important;border-radius:8px!important;font-size:12px!important;box-shadow:0 4px 14px rgba(0,119,182,0.12)!important;padding:5px 10px!important;}.leaflet-light-tooltip::before{border-top-color:rgba(0,180,216,0.25)!important;}`;
    document.head.appendChild(style);

    loadDistrictMarkers();
    setInterval(loadDistrictMarkers, 15*60*1000);

}); // END DOMContentLoaded


/* =============================================
   SIDEBAR RESPONSIVE — overlay + hamburger
   Logic toggle nằm hoàn toàn trong toggleSidebar() ở home.html
   ============================================= */
(function () {
    function init() {
        // Tạo overlay
        let overlay = document.querySelector('.sidebar-overlay');
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.className = 'sidebar-overlay';
            const layout = document.querySelector('.main-layout');
            if (layout) layout.appendChild(overlay);
        }
        overlay.addEventListener('click', function () {
            if (typeof window.toggleSidebar === 'function') window.toggleSidebar();
        });

        // Tạo hamburger button trong navbar
        const navbar = document.querySelector('.navbar');
        if (navbar && !navbar.querySelector('.nav-hamburger')) {
            const hbg = document.createElement('button');
            hbg.className = 'nav-hamburger';
            hbg.setAttribute('aria-label', 'Menu');
            hbg.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>`;
            const logo = navbar.querySelector('.nav-logo');
            if (logo) logo.insertAdjacentElement('afterend', hbg);
            hbg.addEventListener('click', function () {
                if (typeof window.toggleSidebar === 'function') window.toggleSidebar();
            });
        }

        // Auto-close sidebar khi resize lên desktop
        window.addEventListener('resize', function () {
            if (window.innerWidth > 900) {
                const sb  = document.getElementById('sidebarLeft');
                const btn = document.getElementById('sidebarToggle');
                const ov  = document.querySelector('.sidebar-overlay');
                if (sb)  { sb.classList.remove('open'); }
                if (btn) { btn.classList.remove('open'); }
                if (ov)  { ov.classList.remove('show'); }
            }
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();