/**
 * Katindhi Valley General Store - Owner Management Portal
 * Specially tailored for Hitesh Gupta (9418301840)
 */

let AdminState = {
  orders: [],
  activeFilter: 'all',
  searchQuery: ''
};

document.addEventListener('DOMContentLoaded', () => {
  fetchStats();
  fetchOrders();
  setupAdminListeners();
});

async function fetchStats() {
  try {
    const res = await fetch('/api/stats');
    const json = await res.json();
    if (json.success) {
      document.getElementById('stat-total-orders').textContent = json.stats.total_orders;
      document.getElementById('stat-total-sales').textContent = `₹${json.stats.total_sales.toLocaleString('en-IN')}`;
      document.getElementById('stat-pending-orders').textContent = json.stats.pending_orders;
      document.getElementById('stat-products-count').textContent = json.stats.total_products;
    }
  } catch (err) {
    console.error('Error fetching admin stats:', err);
  }
}

async function fetchOrders() {
  const tbody = document.getElementById('admin-orders-tbody');
  if (tbody) {
    tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding: 24px; color:#64748b;">Loading wholesale orders...</td></tr>`;
  }

  try {
    const params = new URLSearchParams();
    if (AdminState.activeFilter && AdminState.activeFilter !== 'all') {
      params.append('status', AdminState.activeFilter);
    }
    if (AdminState.searchQuery) {
      params.append('search', AdminState.searchQuery);
    }

    const res = await fetch(`/api/orders?${params.toString()}`);
    const json = await res.json();
    if (json.success) {
      AdminState.orders = json.orders;
      renderOrders(json.orders);
    }
  } catch (err) {
    console.error('Error fetching orders:', err);
    if (tbody) {
      tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; color:red;">Failed to load orders.</td></tr>`;
    }
  }
}

function renderOrders(orders) {
  const tbody = document.getElementById('admin-orders-tbody');
  if (!tbody) return;

  if (orders.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="7" style="text-align:center; padding: 36px; color:#64748b;">
          No wholesale orders found in this filter.
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = orders.map(o => {
    const waText = encodeURIComponent(`Namaste ${o.customer_name} ji, regarding your order #${o.order_number} at Katindhi Valley General Store (Total: ₹${o.total_amount.toLocaleString('en-IN')}).`);
    const customerWaUrl = `https://wa.me/91${o.phone}?text=${waText}`;

    return `
      <tr>
        <td>
          <strong>${o.order_number}</strong>
          <div style="font-size:0.75rem; color:#64748b;">${o.created_at}</div>
        </td>
        <td>
          <div style="font-weight:700; color:#0f172a;">${o.customer_name}</div>
          ${o.shop_name ? `<div style="font-size:0.8rem; color:#d97706; font-weight:600;">🏢 ${o.shop_name}</div>` : ''}
          <div style="font-size:0.8rem; color:#475569;">📞 ${o.phone}</div>
        </td>
        <td>
          <div style="max-width:220px; font-size:0.82rem; color:#334155; line-height:1.3;">
            ${o.address}
          </div>
          <div style="font-size:0.75rem; color:#0284c7; font-weight:600; margin-top:2px;">
            🚚 ${o.delivery_type} (${o.delivery_slot})
          </div>
        </td>
        <td>
          <div style="font-size:0.85rem; font-weight:600;">${o.items_count} items</div>
          <details style="font-size:0.78rem; color:#64748b; margin-top:2px; cursor:pointer;">
            <summary>View List</summary>
            <div style="background:#f1f5f9; padding:6px; border-radius:6px; margin-top:4px;">
              ${o.items.map(it => `<div>• ${it.name} (${it.packaging}) x ${it.qty}</div>`).join('')}
            </div>
          </details>
        </td>
        <td>
          <div style="font-weight:800; color:#065f46; font-size:0.95rem;">
            ₹${o.total_amount.toLocaleString('en-IN')}
          </div>
          <div style="font-size:0.75rem; color:#64748b;">${o.payment_method}</div>
        </td>
        <td>
          <select class="status-select status-tag ${o.status}" onchange="changeOrderStatus('${o.order_number}', this.value)" style="border: 1px solid #cbd5e1; cursor:pointer; font-weight:700;">
            <option value="Pending" ${o.status === 'Pending' ? 'selected' : ''}>Pending</option>
            <option value="Confirmed" ${o.status === 'Confirmed' ? 'selected' : ''}>Confirmed</option>
            <option value="Dispatched" ${o.status === 'Dispatched' ? 'selected' : ''}>Dispatched</option>
            <option value="Delivered" ${o.status === 'Delivered' ? 'selected' : ''}>Delivered</option>
            <option value="Cancelled" ${o.status === 'Cancelled' ? 'selected' : ''}>Cancelled</option>
          </select>
        </td>
        <td>
          <div style="display:flex; gap:6px; align-items:center;">
            <a href="tel:+91${o.phone}" class="btn-icon-text btn-outline" style="padding:4px 8px; font-size:0.78rem;" title="Call Customer">
              📞 Call
            </a>
            <a href="${customerWaUrl}" target="_blank" class="btn-icon-text btn-outline" style="padding:4px 8px; font-size:0.78rem; color:#15803d; border-color:#86efac;" title="WhatsApp Customer">
              💬 WA
            </a>
            <button onclick="printAdminSlip('${o.order_number}')" class="btn-icon-text btn-outline" style="padding:4px 8px; font-size:0.78rem;" title="Print Delivery Slip">
              🖨️
            </button>
          </div>
        </td>
      </tr>
    `;
  }).join('');
}

async function changeOrderStatus(orderId, newStatus) {
  try {
    const res = await fetch('/api/orders/update-status', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ order_id: orderId, status: newStatus })
    });
    const json = await res.json();
    if (json.success) {
      fetchStats();
      fetchOrders();
    } else {
      alert("Status update failed: " + json.error);
    }
  } catch (err) {
    console.error('Status error:', err);
    alert("Network error updating status.");
  }
}

function filterOrdersByStatus(status, element) {
  AdminState.activeFilter = status;
  document.querySelectorAll('.filter-tab').forEach(t => t.classList.remove('active'));
  if (element) element.classList.add('active');
  fetchOrders();
}

function setupAdminListeners() {
  const searchInput = document.getElementById('admin-order-search');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      AdminState.searchQuery = e.target.value.trim();
      clearTimeout(window._adminSearchTimer);
      window._adminSearchTimer = setTimeout(() => {
        fetchOrders();
      }, 250);
    });
  }

  const addProductForm = document.getElementById('add-product-form');
  if (addProductForm) {
    addProductForm.addEventListener('submit', handleAddProduct);
  }
}

function openAddProductModal() {
  const modal = document.getElementById('add-product-modal');
  if (modal) modal.classList.add('open');
}

function closeAddProductModal() {
  const modal = document.getElementById('add-product-modal');
  if (modal) modal.classList.remove('open');
}

async function handleAddProduct(e) {
  e.preventDefault();
  const payload = {
    name: document.getElementById('prod-name').value.trim(),
    hindi_name: document.getElementById('prod-hindi').value.trim(),
    category: document.getElementById('prod-category').value,
    packaging: document.getElementById('prod-pack').value.trim(),
    wholesale_price: parseFloat(document.getElementById('prod-price').value),
    retail_mrp: parseFloat(document.getElementById('prod-mrp').value),
    moq: parseInt(document.getElementById('prod-moq').value) || 1,
    unit: document.getElementById('prod-unit').value,
    stock: parseInt(document.getElementById('prod-stock').value) || 100,
    image_category: document.getElementById('prod-icon').value,
    description: document.getElementById('prod-desc').value.trim(),
    is_featured: document.getElementById('prod-featured').checked
  };

  try {
    const res = await fetch('/api/products', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const json = await res.json();
    if (json.success) {
      alert("Product added successfully to wholesale catalog!");
      closeAddProductModal();
      document.getElementById('add-product-form').reset();
      fetchStats();
    } else {
      alert("Failed: " + (json.error || "Unknown"));
    }
  } catch (err) {
    console.error('Error adding product:', err);
    alert("Network error.");
  }
}

async function printAdminSlip(orderNumber) {
  try {
    const res = await fetch(`/api/orders/${orderNumber}`);
    const json = await res.json();
    if (json.success && json.order) {
      const o = json.order;
      const printWindow = window.open('', '_blank', 'width=750,height=800');
      printWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
          <title>Packing Slip - ${o.order_number}</title>
          <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; padding: 24px; color: #111; }
            .header { text-align: center; border-bottom: 2px solid #065f46; padding-bottom: 10px; margin-bottom: 16px; }
            .header h2 { margin: 0; color: #065f46; }
            .meta { margin-bottom: 16px; font-size: 14px; line-height: 1.6; }
            table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
            th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
            th { background: #f1f5f9; }
            .total { text-align: right; font-size: 16px; font-weight: bold; }
          </style>
        </head>
        <body>
          <div class="header">
            <h2>KATINDHI VALLEY GENERAL STORE</h2>
            <p><strong>WHOLESALE PACKING & DISPATCH SLIP</strong></p>
            <p>Owner: Hitesh Gupta | 9418301840 | Timings: 8:00 AM - 5:00 PM (Mon-Sat)</p>
          </div>
          <div class="meta">
            <div><strong>Order #:</strong> ${o.order_number} &nbsp;|&nbsp; <strong>Date:</strong> ${o.created_at}</div>
            <div><strong>Customer:</strong> ${o.customer_name} ${o.shop_name ? `(${o.shop_name})` : ''}</div>
            <div><strong>Phone:</strong> ${o.phone}</div>
            <div><strong>Delivery Address:</strong> ${o.address}</div>
            <div><strong>Slot & Mode:</strong> ${o.delivery_type} - ${o.delivery_slot}</div>
            <div><strong>Payment Mode:</strong> ${o.payment_method} &nbsp;|&nbsp; <strong>Status:</strong> ${o.status}</div>
          </div>
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>Item Name</th>
                <th>Pack Size</th>
                <th>Qty</th>
                <th>Wholesale Rate</th>
                <th>Line Total</th>
              </tr>
            </thead>
            <tbody>
              ${o.items.map((it, i) => `
                <tr>
                  <td>${i + 1}</td>
                  <td><strong>${it.name}</strong></td>
                  <td>${it.packaging}</td>
                  <td><strong>${it.qty}</strong></td>
                  <td>₹${it.wholesale_price.toFixed(2)}</td>
                  <td>₹${(it.wholesale_price * it.qty).toFixed(2)}</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
          <div class="total">
            Total Wholesale Payable: ₹${o.total_amount.toLocaleString('en-IN', {minimumFractionDigits: 2})}
          </div>
          ${o.notes ? `<p style="margin-top:14px;"><strong>Customer Note:</strong> ${o.notes}</p>` : ''}
          <div style="margin-top: 40px; display:flex; justify-content:space-between; font-size: 13px;">
            <div>Prepared By: __________________</div>
            <div>Checked By: __________________</div>
            <div>Received By: __________________</div>
          </div>
          <script>window.onload = function() { window.print(); };</script>
        </body>
        </html>
      `);
      printWindow.document.close();
    }
  } catch (e) {
    console.error('Print slip error', e);
  }
}
