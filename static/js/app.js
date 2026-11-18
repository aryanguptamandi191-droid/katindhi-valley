/**
 * Katindhi Valley General Store - Wholesale Grocery App
 * Owner: Hitesh Gupta (9418301840)
 * Direct WhatsApp & Phone Ordering for Customers
 */

// Application State
const State = {
  storeInfo: null,
  categories: [],
  products: [],
  activeCategory: 'all',
  searchQuery: '',
  sortOrder: 'default'
};

const STORE_PHONE = "9418301840";
const STORE_WA_NUMBER = "919418301840";

// Category Icons Mapping
const categoryIcons = {
  "Grains & Flours": "🌾",
  "Pulses & Dals": "🥣",
  "Edible Oils & Ghee": "🛢️",
  "Sugar & Salt": "🧂",
  "Spices & Masala": "🌶️",
  "Tea & Packaged": "☕",
  "Cleaning & Household": "🧼",
  "Dry Fruits & Nuts": "🥜",
  "all": "🏪"
};

// Product Visual Icon Fallback
const productTypeIcons = {
  "grain": "🌾",
  "pulse": "🥣",
  "oil": "🛢️",
  "sugar": "🧂",
  "spice": "🌶️",
  "tea": "☕",
  "cleaning": "🧼",
  "dryfruit": "🥜"
};

// Initialize Application
document.addEventListener('DOMContentLoaded', () => {
  fetchStoreInfo();
  fetchCategories();
  fetchProducts();
  setupEventListeners();
});

// -----------------------------------------------------------------------------
// API Calls
// -----------------------------------------------------------------------------

async function fetchStoreInfo() {
  try {
    const res = await fetch('/api/store-info');
    const json = await res.json();
    if (json.success) {
      State.storeInfo = json.data;
      renderStoreInfo(json.data);
    }
  } catch (err) {
    console.error('Error fetching store info:', err);
  }
}

async function fetchCategories() {
  try {
    const res = await fetch('/api/categories');
    const json = await res.json();
    if (json.success) {
      State.categories = json.categories;
      renderCategories(json.categories);
    }
  } catch (err) {
    console.error('Error fetching categories:', err);
  }
}

async function fetchProducts() {
  const container = document.getElementById('products-grid');
  if (container) {
    container.innerHTML = `
      <div style="grid-column: 1 / -1; text-align: center; padding: 40px; color: #64748b;">
        <div style="font-size: 2rem; margin-bottom: 10px;">⏳</div>
        <p>Loading fresh grocery catalog...</p>
      </div>
    `;
  }

  try {
    const params = new URLSearchParams();
    if (State.activeCategory && State.activeCategory !== 'all') {
      params.append('category', State.activeCategory);
    }
    if (State.searchQuery) {
      params.append('search', State.searchQuery);
    }
    if (State.sortOrder && State.sortOrder !== 'default') {
      params.append('sort', State.sortOrder);
    }

    const res = await fetch(`/api/products?${params.toString()}`);
    const json = await res.json();
    if (json.success) {
      State.products = json.products;
      renderProducts(json.products);
      const countEl = document.getElementById('product-count-display');
      if (countEl) countEl.textContent = `${json.count} grocery items available`;
    }
  } catch (err) {
    console.error('Error fetching products:', err);
    if (container) {
      container.innerHTML = `<div style="grid-column: 1 / -1; text-align: center; color: red;">Failed to load products. Please refresh.</div>`;
    }
  }
}

// -----------------------------------------------------------------------------
// Rendering Functions
// -----------------------------------------------------------------------------

function renderStoreInfo(info) {
  // Update Top Bar & Status Elements
  const statusBadge = document.getElementById('top-status-badge');
  if (statusBadge) {
    statusBadge.innerHTML = `
      <span class="status-dot ${info.is_open ? '' : 'closed'}"></span>
      <span>${info.status_text}</span>
    `;
  }

  const liveNotice = document.getElementById('store-live-notice');
  if (liveNotice) {
    liveNotice.textContent = info.notice;
  }

  const timingsDisplay = document.getElementById('hero-timings-display');
  if (timingsDisplay) {
    timingsDisplay.textContent = `${info.timings} (${info.operating_days})`;
  }

  const ownerDisplay = document.getElementById('hero-owner-display');
  if (ownerDisplay) {
    ownerDisplay.textContent = `${info.owner} • ${info.phone}`;
  }

  // Bind WhatsApp Order links
  const defaultMsg = encodeURIComponent("Namaste Hitesh ji, I am contacting you from Katindhi Valley General Store website to place an order.");
  const waUrl = `https://wa.me/${STORE_WA_NUMBER}?text=${defaultMsg}`;
  
  document.querySelectorAll('.dynamic-wa-link').forEach(el => {
    el.href = waUrl;
  });

  document.querySelectorAll('.dynamic-tel-link').forEach(el => {
    el.href = `tel:+91${STORE_PHONE}`;
  });
}

function renderCategories(categories) {
  const container = document.getElementById('category-scroll-container');
  if (!container) return;

  const totalItems = categories.reduce((acc, cat) => acc + cat.count, 0);

  let html = `
    <button class="category-pill ${State.activeCategory === 'all' ? 'active' : ''}" onclick="selectCategory('all')">
      <span>🏪</span>
      <span>All Products</span>
      <span class="category-count">${totalItems}</span>
    </button>
  `;

  categories.forEach(cat => {
    const icon = categoryIcons[cat.name] || '📦';
    const isActive = State.activeCategory === cat.name ? 'active' : '';
    html += `
      <button class="category-pill ${isActive}" onclick="selectCategory('${cat.name.replace(/'/g, "\\'")}')">
        <span>${icon}</span>
        <span>${cat.name}</span>
        <span class="category-count">${cat.count}</span>
      </button>
    `;
  });

  container.innerHTML = html;
}

function renderProducts(products) {
  const container = document.getElementById('products-grid');
  if (!container) return;

  if (products.length === 0) {
    container.innerHTML = `
      <div style="grid-column: 1 / -1; text-align: center; padding: 60px 20px; background: white; border-radius: 16px; border: 1px solid #e2e8f0;">
        <div style="font-size: 3rem; margin-bottom: 12px;">🔍</div>
        <h3 style="font-size: 1.2rem; color: #1e293b; margin-bottom: 6px;">No items found</h3>
        <p style="color: #64748b; font-size: 0.9rem;">Try searching for another grocery product or touch our phone number to inquire directly.</p>
        <div style="margin-top: 16px; display: flex; justify-content: center; gap: 10px;">
          <button onclick="resetFilters()" class="btn-icon-text btn-outline">
            View All Products
          </button>
          <a href="https://wa.me/${STORE_WA_NUMBER}?text=${encodeURIComponent('Namaste Hitesh ji, I am looking for a grocery item.')}" target="_blank" class="btn-icon-text btn-header-wa">
            💬 Ask on WhatsApp
          </a>
        </div>
      </div>
    `;
    return;
  }

  container.innerHTML = products.map(prod => {
    const icon = productTypeIcons[prod.image_category] || '📦';
    
    // Pre-filled WhatsApp message for this item
    const itemMsg = encodeURIComponent(
      `Namaste Hitesh ji, I want to order from Katindhi Valley General Store:\n` +
      `📦 Item: *${prod.name}*\n` +
      `⚖️ Pack: *${prod.packaging}*\n` +
      `💰 Rate: *₹${prod.wholesale_price.toLocaleString('en-IN')}*\n` +
      `Please let me know availability and delivery timing.`
    );
    const itemWaUrl = `https://wa.me/${STORE_WA_NUMBER}?text=${itemMsg}`;

    return `
      <div class="product-card" id="product-${prod.id}">
        <div class="product-card-top">
          ${prod.is_featured ? `<span class="badge-featured">Valley Special</span>` : ''}
          <div class="product-icon-display">${icon}</div>
          <span class="badge-packaging">📦 ${prod.packaging}</span>
        </div>

        <div class="product-body">
          <div class="product-category-tag">${prod.category}</div>
          <h3 class="product-title">${prod.name}</h3>
          ${prod.hindi_name ? `<div class="product-hindi">${prod.hindi_name}</div>` : ''}
          <p class="product-desc" title="${prod.description || ''}">${prod.description || 'Fresh quality grocery pack available at store.'}</p>

          <div class="pricing-block">
            <div class="price-main">
              <span class="wholesale-rate">₹${prod.wholesale_price.toLocaleString('en-IN')}</span>
              <span class="rate-unit">per ${prod.packaging}</span>
            </div>
          </div>

          <!-- Direct Touch to WhatsApp Order -->
          <a href="${itemWaUrl}" target="_blank" class="btn-card-wa" title="Touch to order this item on WhatsApp">
            <span style="font-size: 1.15rem;">💬</span>
            <span>Order on WhatsApp</span>
          </a>
        </div>
      </div>
    `;
  }).join('');
}

// -----------------------------------------------------------------------------
// Filter & Search Handlers
// -----------------------------------------------------------------------------

function selectCategory(categoryName) {
  State.activeCategory = categoryName;
  const pills = document.querySelectorAll('.category-pill');
  pills.forEach(p => p.classList.remove('active'));

  const activePill = Array.from(pills).find(p => {
    if (categoryName === 'all' && p.textContent.includes('All Products')) return true;
    return p.textContent.includes(categoryName);
  });
  if (activePill) activePill.classList.add('active');

  fetchProducts();
}

function handleSearch(e) {
  const query = e.target.value.trim();
  State.searchQuery = query;
  clearTimeout(window._searchTimer);
  window._searchTimer = setTimeout(() => {
    fetchProducts();
  }, 250);
}

function handleSortChange(e) {
  State.sortOrder = e.target.value;
  fetchProducts();
}

function resetFilters() {
  State.activeCategory = 'all';
  State.searchQuery = '';
  State.sortOrder = 'default';
  const searchInput = document.getElementById('search-input');
  if (searchInput) searchInput.value = '';
  const sortSelect = document.getElementById('sort-select');
  if (sortSelect) sortSelect.value = 'default';
  renderCategories(State.categories);
  fetchProducts();
}

// -----------------------------------------------------------------------------
// Rate Card Modal (Without Distributor Margins)
// -----------------------------------------------------------------------------

function openRateCardModal() {
  const modal = document.getElementById('rate-card-modal');
  if (!modal) return;

  const tbody = document.getElementById('rate-card-table-body');
  if (tbody) {
    tbody.innerHTML = State.products.map(p => {
      const waMsg = encodeURIComponent(`Namaste Hitesh ji, I want to order *${p.name}* (${p.packaging}) at ₹${p.wholesale_price.toLocaleString('en-IN')}.`);
      return `
        <tr>
          <td style="font-weight:600; padding:10px 8px;">
            ${p.name}
            ${p.hindi_name ? `<div style="color:#64748b; font-size:0.8rem;">${p.hindi_name}</div>` : ''}
          </td>
          <td style="padding:10px 8px; color:#475569;">${p.category}</td>
          <td style="padding:10px 8px;"><strong>${p.packaging}</strong></td>
          <td style="padding:10px 8px; color:#065f46; font-weight:800; font-size:0.95rem;">₹${p.wholesale_price.toLocaleString('en-IN')}</td>
          <td style="padding:10px 8px; text-align:right;">
            <a href="https://wa.me/${STORE_WA_NUMBER}?text=${waMsg}" target="_blank" class="btn-icon-text" style="background:#25d366; color:white; padding:5px 10px; font-size:0.78rem; text-decoration:none; border-radius:6px;">
              💬 Order
            </a>
          </td>
        </tr>
      `;
    }).join('');
  }

  modal.classList.add('open');
}

function closeRateCardModal() {
  const modal = document.getElementById('rate-card-modal');
  if (modal) modal.classList.remove('open');
}

// -----------------------------------------------------------------------------
// Event Listeners
// -----------------------------------------------------------------------------

function setupEventListeners() {
  const searchInput = document.getElementById('search-input');
  if (searchInput) searchInput.addEventListener('input', handleSearch);

  const sortSelect = document.getElementById('sort-select');
  if (sortSelect) sortSelect.addEventListener('change', handleSortChange);

  // Close modals on backdrop click
  document.querySelectorAll('.modal-overlay').forEach(modal => {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        modal.classList.remove('open');
      }
    });
  });
}
