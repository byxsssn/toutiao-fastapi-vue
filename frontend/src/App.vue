<script setup>
import { computed, onMounted, ref } from "vue";

const categories = ref([]);
const selectedCategoryId = ref("");
const articles = ref([]);
const categoryLoading = ref(false);
const articleLoading = ref(false);
const error = ref("");
const page = ref(1);
const pageSize = ref(10);
const total = ref(0);
const hasMore = ref(false);
const view = ref("list");
const detail = ref(null);
const detailLoading = ref(false);
const detailError = ref("");
const favoriteLoading = ref(false);
const isCurrentFavorite = ref(false);
const authMode = ref("login");
const authLoading = ref(false);
const authMessage = ref("");
const authError = ref("");
const authToken = ref("");
const userInfo = ref(null);
const userForm = ref({
  username: "",
  password: "",
});
const passwordLoading = ref(false);
const passwordMessage = ref("");
const passwordError = ref("");
const passwordForm = ref({
  oldPassword: "",
  newPassword: "",
});

const activeCategory = computed(() =>
  categories.value.find((item) => String(item.id) === selectedCategoryId.value),
);

const authStatusText = computed(() => {
  if (authLoading.value) {
    return authMode.value === "login" ? "正在登录..." : "正在注册...";
  }

  return authError.value || authMessage.value;
});

const authStatusClass = computed(() => ({
  error: Boolean(authError.value),
  success: Boolean(authMessage.value),
}));

const statusText = computed(() => {
  if (categoryLoading.value || articleLoading.value) {
    return "加载中";
  }

  if (error.value) {
    return error.value;
  }

  return activeCategory.value ? `${activeCategory.value.name}频道 · ${total.value}条` : "请选择频道";
});

function formatDate(value) {
  if (!value) {
    return "";
  }

  return new Date(value).toLocaleDateString("zh-CN", {
    month: "2-digit",
    day: "2-digit",
  });
}

function formatDetailDate(value) {
  if (!value) {
    return "";
  }

  return new Date(value).toLocaleString("zh-CN", {
    hour12: false,
  });
}

function thumbnailClass(index) {
  return `thumb thumb-${(index % 6) + 1}`;
}

async function loadCategories() {
  categoryLoading.value = true;
  error.value = "";

  try {
    const response = await fetch("/api/news/?limit=100");
    const result = await readJson(response);

    if (!response.ok || result.code !== 200) {
      throw new Error(result.message || "分类接口请求失败");
    }

    categories.value = result.data;

    if (!selectedCategoryId.value && result.data.length > 0) {
      selectedCategoryId.value = String(result.data[0].id);
    }

    if (selectedCategoryId.value) {
      await loadArticles();
    }
  } catch (err) {
    error.value = err.message;
  } finally {
    categoryLoading.value = false;
  }
}

async function loadArticles(append = false) {
  if (!selectedCategoryId.value) {
    articles.value = [];
    total.value = 0;
    hasMore.value = false;
    return;
  }

  articleLoading.value = true;
  error.value = "";

  const query = new URLSearchParams({
    categoryId: selectedCategoryId.value,
    page: String(page.value),
    pageSize: String(pageSize.value),
  });

  try {
    const response = await fetch(`/api/news/list?${query.toString()}`);
    const result = await readJson(response);

    if (!response.ok || result.code !== 200) {
      throw new Error(result.message || "新闻列表接口请求失败");
    }

    articles.value = append
      ? [...articles.value, ...result.data.list]
      : result.data.list;
    total.value = result.data.total;
    hasMore.value = result.data.hasMore;
  } catch (err) {
    error.value = err.message;
  } finally {
    articleLoading.value = false;
  }
}

async function openDetail(id) {
  detailLoading.value = true;
  detailError.value = "";
  isCurrentFavorite.value = false;
  view.value = "detail";

  try {
    const response = await fetch(`/api/news/detail?id=${id}`);
    const result = await readJson(response);

    if (!response.ok || result.code !== 200) {
      throw new Error(result.message || result.detail || "新闻详情接口请求失败");
    }

    detail.value = result.data;
    await loadFavoriteStatus(result.data.id);
  } catch (err) {
    detail.value = null;
    detailError.value = err.message;
  } finally {
    detailLoading.value = false;
  }
}

async function loadFavoriteStatus(newsId) {
  if (!authToken.value) {
    return;
  }

  const query = new URLSearchParams({ newsId: String(newsId) });
  try {
    const response = await fetch(`/api/favorites/check?${query.toString()}`, {
      headers: {
        Authorization: `Bearer ${authToken.value}`,
      },
    });
    const result = await readJson(response);

    if (!response.ok || result.code !== 200) {
      throw new Error(result.message || "检查收藏失败");
    }

    isCurrentFavorite.value = result.data.isFavorite;
  } catch (err) {
    detailError.value = err.message;
  }
}

async function toggleFavorite() {
  if (!detail.value) {
    return;
  }

  if (!authToken.value) {
    detailError.value = "请先登录再收藏";
    return;
  }

  favoriteLoading.value = true;
  detailError.value = "";

  const query = new URLSearchParams({ newsId: String(detail.value.id) });
  const method = isCurrentFavorite.value ? "DELETE" : "POST";
  try {
    const response = await fetch(
      method === "DELETE" ? `/api/favorites/?${query.toString()}` : "/api/favorites/",
      {
        method,
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${authToken.value}`,
        },
        body: method === "POST"
          ? JSON.stringify({ newsId: detail.value.id })
          : undefined,
      },
    );
    const result = await readJson(response);

    if (!response.ok || result.code !== 200) {
      throw new Error(result.message || "收藏操作失败");
    }

    isCurrentFavorite.value = result.data.isFavorite;
  } catch (err) {
    detailError.value = err.message;
  } finally {
    favoriteLoading.value = false;
  }
}

async function submitAuth() {
  authLoading.value = true;
  authMessage.value = "";
  authError.value = "";
  authToken.value = "";

  const isLogin = authMode.value === "login";
  const url = isLogin ? "/api/users/login" : "/api/users/";

  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(userForm.value),
    });
    const result = await readJson(response);

    if (!response.ok || result.code !== 200) {
      throw new Error(result.message || "操作失败");
    }

    userInfo.value = result.data.userinfo;
    authToken.value = result.data.token;
    authMessage.value = `${isLogin ? "登录" : "注册"}成功`;
    userForm.value.password = "";
    await loadUserInfo();
  } catch (err) {
    authError.value = err.message;
  } finally {
    authLoading.value = false;
  }
}

async function loadUserInfo() {
  if (!authToken.value) {
    authError.value = "请先登录";
    return;
  }

  try {
    const response = await fetch("/api/users/info", {
      headers: {
        Authorization: `Bearer ${authToken.value}`,
      },
    });
    const result = await readJson(response);

    if (!response.ok || result.code !== 200) {
      throw new Error(result.message || "获取用户信息失败");
    }

    userInfo.value = result.data;
    authMessage.value = "用户信息已更新";
    authError.value = "";
  } catch (err) {
    authError.value = err.message;
  }
}

async function changePassword() {
  if (!authToken.value) {
    passwordError.value = "请先登录";
    return;
  }

  passwordLoading.value = true;
  passwordMessage.value = "";
  passwordError.value = "";

  try {
    const response = await fetch("/api/users/password", {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${authToken.value}`,
      },
      body: JSON.stringify(passwordForm.value),
    });
    const result = await readJson(response);

    if (!response.ok || result.code !== 200) {
      throw new Error(result.message || "修改密码失败");
    }

    userInfo.value = result.data.userinfo;
    authToken.value = result.data.token;
    passwordMessage.value = "密码修改成功，请使用新密码登录";
    passwordForm.value.oldPassword = "";
    passwordForm.value.newPassword = "";
  } catch (err) {
    passwordError.value = err.message;
  } finally {
    passwordLoading.value = false;
  }
}

async function readJson(response) {
  const text = await response.text();

  if (!text) {
    throw new Error("接口返回空内容，请确认 FastAPI 后端已启动");
  }

  try {
    return JSON.parse(text);
  } catch {
    throw new Error(`接口返回的不是 JSON，HTTP 状态码：${response.status}`);
  }
}

function backToList() {
  view.value = "list";
  detailError.value = "";
}

function openProfile() {
  view.value = "profile";
  authMessage.value = "";
  authError.value = "";
  passwordMessage.value = "";
  passwordError.value = "";
}

function switchAuthMode(mode) {
  authMode.value = mode;
  authMessage.value = "";
  authError.value = "";
  authToken.value = "";
  userInfo.value = null;
  passwordMessage.value = "";
  passwordError.value = "";
}

function selectCategory(id) {
  selectedCategoryId.value = String(id);
  page.value = 1;
  view.value = "list";
  loadArticles();
}

function refreshCurrent() {
  if (view.value === "profile") {
    return;
  }

  if (selectedCategoryId.value) {
    page.value = 1;
    loadArticles();
  } else {
    loadCategories();
  }
}

function loadMore() {
  if (!hasMore.value || articleLoading.value) {
    return;
  }

  page.value += 1;
  loadArticles(true);
}

onMounted(loadCategories);
</script>

<template>
  <main class="phone-shell">
    <section v-if="view === 'list'" class="phone-screen">
      <header class="app-header">
        <button
          class="ghost-button"
          type="button"
          title="刷新"
          aria-label="刷新新闻"
          :disabled="categoryLoading || articleLoading"
          @click="refreshCurrent"
        >
          ↻
        </button>
        <h1>新闻资讯</h1>
        <button class="ghost-button" type="button" title="更多" aria-label="更多">
          ⋯
        </button>
      </header>

      <nav class="category-tabs" aria-label="新闻分类">
        <button
          v-for="item in categories"
          :key="item.id"
          type="button"
          :class="{ active: String(item.id) === selectedCategoryId }"
          @click="selectCategory(item.id)"
        >
          {{ item.name }}
        </button>
        <button type="button" class="more-tab">更多 ›</button>
      </nav>

      <div class="feed-status">
        {{ statusText }}
      </div>

      <section class="feed-list">
        <article
          v-for="(item, index) in articles"
          :key="item.id"
          class="news-card"
          @click="openDetail(item.id)"
        >
          <div class="news-copy">
            <h2>{{ item.title }}</h2>
            <p>{{ item.description }}</p>
            <div class="news-meta">
              <span>{{ item.category || activeCategory?.name || "新闻" }}</span>
              <span>{{ item.views }} 阅读</span>
              <span>{{ formatDate(item.created_at) }}</span>
            </div>
          </div>
          <div :class="thumbnailClass(index)" aria-hidden="true">
            <span>{{ item.category || "新闻" }}</span>
          </div>
        </article>

        <div v-if="articleLoading" class="empty-state">正在加载新闻...</div>
        <div v-else-if="articles.length === 0" class="empty-state">暂无新闻内容</div>
      </section>

      <button v-if="hasMore" class="load-more" type="button" @click="loadMore">
        加载更多
      </button>

      <footer class="bottom-nav">
        <button type="button" class="active" @click="backToList">
          <span>⌂</span>
          首页
        </button>
        <button type="button">
          <span>◌</span>
          AI问答
        </button>
        <button type="button" @click="openProfile">
          <span>♙</span>
          我的
        </button>
      </footer>
    </section>

    <section v-else-if="view === 'detail'" class="phone-screen detail-screen">
      <header class="detail-header">
        <button class="back-button" type="button" @click="backToList">‹ 返回</button>
        <h1>新闻详情</h1>
        <button
          class="favorite-button"
          type="button"
          :class="{ active: isCurrentFavorite }"
          :disabled="favoriteLoading"
          :title="isCurrentFavorite ? '取消收藏' : '收藏'"
          :aria-label="isCurrentFavorite ? '取消收藏' : '收藏'"
          @click="toggleFavorite"
        >
          {{ isCurrentFavorite ? "★" : "☆" }}
        </button>
      </header>

      <section v-if="detailLoading" class="detail-state">正在加载详情...</section>
      <section v-else-if="detailError" class="detail-state">{{ detailError }}</section>

      <article v-else-if="detail" class="detail-body">
        <h2>{{ detail.title }}</h2>
        <div class="detail-meta">
          <span>{{ detail.author || "新闻" }}</span>
          <span>{{ formatDetailDate(detail.publishTime) }}</span>
          <span>{{ detail.views }} 阅读</span>
        </div>

        <div class="detail-image thumb-3" aria-hidden="true">
          <span>{{ detail.author || "新闻" }}</span>
        </div>

        <p class="detail-content">{{ detail.content }}</p>

        <div class="related-block">
          <h3>相关推荐</h3>
          <button
            v-for="(item, index) in detail.relatedNews"
            :key="item.id"
            class="related-item"
            type="button"
            @click="openDetail(item.id)"
          >
            <span :class="thumbnailClass(index)"></span>
            <strong>{{ item.title }}</strong>
          </button>
          <div v-if="detail.relatedNews.length === 0" class="empty-state">暂无相关推荐</div>
        </div>
      </article>
    </section>

    <section v-else class="phone-screen profile-screen">
      <header class="app-header">
        <button class="ghost-button" type="button" title="返回首页" aria-label="返回首页" @click="backToList">
          ‹
        </button>
        <h1>我的</h1>
        <button class="ghost-button" type="button" title="更多" aria-label="更多">⋯</button>
      </header>

      <section class="profile-panel">
        <div class="profile-avatar">
          {{ userInfo?.username?.slice(0, 1).toUpperCase() || "我" }}
        </div>
        <h2>{{ userInfo ? userInfo.username : "登录或注册账号" }}</h2>
        <p>{{ userInfo ? "已经拿到后端返回的用户信息和 token" : "这里会调用 FastAPI 的用户接口" }}</p>
      </section>

      <p v-if="authStatusText" class="auth-status" :class="authStatusClass">
        {{ authStatusText }}
      </p>

      <div class="auth-switch" aria-label="账号操作">
        <button
          type="button"
          :class="{ active: authMode === 'login' }"
          @click="switchAuthMode('login')"
        >
          登录
        </button>
        <button
          type="button"
          :class="{ active: authMode === 'register' }"
          @click="switchAuthMode('register')"
        >
          注册
        </button>
      </div>

      <form class="register-form" @submit.prevent="submitAuth">
        <label>
          用户名
          <input v-model.trim="userForm.username" type="text" required placeholder="请输入用户名" />
        </label>
        <label>
          密码
          <input v-model="userForm.password" type="password" required placeholder="请输入密码" />
        </label>

        <button type="submit" :disabled="authLoading">
          {{ authLoading ? "提交中..." : authMode === "login" ? "登录" : "注册" }}
        </button>
      </form>

      <p v-if="authToken" class="form-message success">
        <span v-if="authToken">token：{{ authToken }}</span>
      </p>

      <button
        v-if="authToken"
        class="profile-action"
        type="button"
        :disabled="authLoading"
        @click="loadUserInfo"
      >
        刷新我的信息
      </button>

      <form v-if="authToken" class="register-form" @submit.prevent="changePassword">
        <label>
          旧密码
          <input
            v-model="passwordForm.oldPassword"
            type="password"
            required
            placeholder="请输入旧密码"
          />
        </label>
        <label>
          新密码
          <input
            v-model="passwordForm.newPassword"
            type="password"
            minlength="6"
            required
            placeholder="至少 6 位"
          />
        </label>

        <button type="submit" :disabled="passwordLoading">
          {{ passwordLoading ? "修改中..." : "修改密码" }}
        </button>
      </form>

      <p v-if="passwordError" class="form-message error">{{ passwordError }}</p>
      <p v-if="passwordMessage" class="form-message success">{{ passwordMessage }}</p>

      <footer class="bottom-nav">
        <button type="button" @click="backToList">
          <span>⌂</span>
          首页
        </button>
        <button type="button">
          <span>◌</span>
          AI问答
        </button>
        <button type="button" class="active">
          <span>♙</span>
          我的
        </button>
      </footer>
    </section>
  </main>
</template>
