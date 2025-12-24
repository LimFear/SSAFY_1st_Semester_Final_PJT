<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useRouter } from "vue-router";
import api from "@/api/axios";
import { useAuthStore } from "@/stores/authStore";

const router = useRouter();
const authStore = useAuthStore();

const isLoggedIn = computed(() => authStore.isLogined === true);

/* =========================
  공용: book 필드 안전 처리
========================= */
function getBookId(book) {
  return book?.id ?? book?.pk ?? book?.book_id ?? book?.bookId ?? null;
}

function getCoverUrl(book) {
  return (
    book?.cover ??
    book?.cover_img ??
    book?.coverImage ??
    book?.image ??
    book?.thumbnail ??
    ""
  );
}

function getTitle(book) {
  return book?.title ?? "(제목 없음)";
}

function getAuthor(book) {
  return book?.author ?? "";
}

function goArticle(book) {
  const bookId = getBookId(book);
  if (!bookId) {
    window.alert("book id가 없습니다.");
    return;
  }
  router.push({ name: "article", params: { id: String(bookId) } });
}

function goList() {
  router.push({ name: "list" });
}

function goLogin() {
  router.push({ name: "login" });
}

/* =========================
  공용 캐러셀 로직
  - template에서 nested ref는 자동 언랩 안되므로 .value 필요
========================= */
function useCarousel(itemsRef, intervalMs = 3200) {
  const activeIndex = ref(0);
  const isPaused = ref(false);
  const timerId = ref(null);

  function stop() {
    if (timerId.value !== null) {
      clearInterval(timerId.value);
      timerId.value = null;
    }
  }

  function start() {
    stop();
    timerId.value = setInterval(() => {
      const length = itemsRef.value.length;
      if (length <= 1) return;
      if (isPaused.value) return;

      activeIndex.value = (activeIndex.value + 1) % length;
    }, intervalMs);
  }

  function pause() {
    isPaused.value = true;
  }
  function resume() {
    isPaused.value = false;
  }

  function focus(index) {
    const length = itemsRef.value.length;
    if (length <= 0) return;
    activeIndex.value = index;
  }

  function getDelta(index) {
    const length = itemsRef.value.length;
    if (length <= 0) return 0;

    let delta = (index - activeIndex.value) % length;
    if (delta < 0) delta += length;
    return delta;
  }

  // 0=center, 1=right, length-1=left
  function getStyle(index) {
    const length = itemsRef.value.length;

    const style = {
      "--tx": "0px",
      "--scale": "0.7",
      "--op": "0",
      "--ry": "0deg",
      "--z": "0",
      pointerEvents: "none",
    };

    if (length <= 0) return style;

    const delta = getDelta(index);

    if (delta === 0) {
      style["--tx"] = "0px";
      style["--scale"] = "1.08";
      style["--op"] = "1";
      style["--ry"] = "0deg";
      style["--z"] = "30";
      style.pointerEvents = "auto";
      return style;
    }

    if (delta === 1) {
      style["--tx"] = "var(--shift)";
      style["--scale"] = "0.86";
      style["--op"] = "0.94";
      style["--ry"] = "-10deg";
      style["--z"] = "20";
      style.pointerEvents = "auto";
      return style;
    }

    if (delta === length - 1) {
      style["--tx"] = "calc(var(--shift) * -1)";
      style["--scale"] = "0.86";
      style["--op"] = "0.94";
      style["--ry"] = "10deg";
      style["--z"] = "20";
      style.pointerEvents = "auto";
      return style;
    }

    return style;
  }

  onBeforeUnmount(stop);

  return { activeIndex, start, stop, pause, resume, focus, getStyle };
}

/* =========================
  인기 TOP5
========================= */
const popularBooks = ref([]);
const popularLoading = ref(false);
const popularError = ref("");

const popularCarousel = useCarousel(popularBooks, 3200);

/* =========================
  추천 TOP5
========================= */
const recommendedBooks = ref([]);
const recommendedLoading = ref(false);
const recommendedError = ref("");

const recommendedCarousel = useCarousel(recommendedBooks, 3200);

async function fetchPopularTop5() {
  popularLoading.value = true;
  popularError.value = "";

  try {
    // ✅ baseURL이 /api/v1이면 앞에 '/' 붙이지 마세요.
    const response = await api.get("articles/books/popular/");
    const data = response.data;
    popularBooks.value = Array.isArray(data) ? data : data?.results ?? [];

    popularCarousel.activeIndex.value = 0;
    popularCarousel.start();
  } catch (e) {
    popularBooks.value = [];
    popularError.value = "인기 도서를 불러오지 못했습니다.";
    popularCarousel.stop();
  } finally {
    popularLoading.value = false;
  }
}

function setRecommendedAsPopular() {
  // 로그인 전(or 실패) fallback
  recommendedBooks.value = [...popularBooks.value];
  recommendedCarousel.activeIndex.value = 0;
  recommendedCarousel.start();
}

async function fetchRecommendedTop5() {
  recommendedLoading.value = true;
  recommendedError.value = "";

  try {
    const response = await api.get("articles/books/recommended/");
    const data = response.data;
    const list = Array.isArray(data) ? data : data?.results ?? [];
    recommendedBooks.value = list;

    // 혹시 빈 리스트면 프론트에서도 fallback
    if (recommendedBooks.value.length === 0) {
      setRecommendedAsPopular();
      return;
    }

    recommendedCarousel.activeIndex.value = 0;
    recommendedCarousel.start();
  } catch (e) {
    // 401/서버에러 등: 인기 TOP5로 fallback
    setRecommendedAsPopular();
  } finally {
    recommendedLoading.value = false;
  }
}

/* 로그인 상태 변경 시 추천 갱신 */
watch(
  () => isLoggedIn.value,
  async (logged) => {
    if (!popularBooks.value.length) return;

    if (logged) {
      await fetchRecommendedTop5();
    } else {
      setRecommendedAsPopular();
    }
  }
);

/* 인기 TOP5 로드되면 로그인 전 추천은 인기 복제본으로 시작 */
watch(
  () => popularBooks.value,
  (val) => {
    if (!val || val.length === 0) return;
    if (!isLoggedIn.value) setRecommendedAsPopular();
  }
);

onMounted(async () => {
  await fetchPopularTop5();
  if (isLoggedIn.value) {
    await fetchRecommendedTop5();
  }
});

/* 타이머 정리 */
onBeforeUnmount(() => {
  popularCarousel.stop();
  recommendedCarousel.stop();
});
</script>

<template>
  <main class="page">
    <!-- HERO -->
    <section class="hero">
      <div class="heroLeft">
        <h1 class="heroTitle">Library</h1>
        <p class="heroDesc">조회수와 댓글 기반으로 인기 도서를 보여드립니다.</p>

        <div class="heroActions">
          <button class="primaryBtn" type="button" @click="goList">
            도서 목록 보기
          </button>
        </div>
      </div>

      <div class="heroRight">
        <div class="heroStat">
          <div class="heroStatTitle">인기 TOP5</div>
          <div class="heroStatDesc">정렬 기준: 조회수 + 댓글 수</div>
        </div>
      </div>
    </section>

    <!-- =========================
      인기 TOP5
    ========================= -->
    <section class="section">
      <div class="sectionHeader">
        <h2 class="sectionTitle">인기 도서 TOP5</h2>
        <p class="sectionSub">인기있는 도서를 확인하세요!</p>
      </div>

      <p v-if="popularError" class="error">{{ popularError }}</p>

      <div
        class="carousel"
        @mouseenter="popularCarousel.pause"
        @mouseleave="popularCarousel.resume"
      >
        <div v-if="popularLoading" class="carouselStage">
          <div
            class="carouselCard skeletonCard"
            style="
              --tx: calc(var(--shift) * -1);
              --scale: 0.86;
              --op: 0.94;
              --ry: 10deg;
              --z: 20;
            "
          />
          <div
            class="carouselCard skeletonCard"
            style="--tx: 0px; --scale: 1.08; --op: 1; --ry: 0deg; --z: 30"
          />
          <div
            class="carouselCard skeletonCard"
            style="
              --tx: var(--shift);
              --scale: 0.86;
              --op: 0.94;
              --ry: -10deg;
              --z: 20;
            "
          />
        </div>

        <div v-else class="carouselStage">
          <button
            v-for="(book, i) in popularBooks"
            :key="(getBookId(book) ?? i) + '-popular'"
            class="carouselCard"
            type="button"
            :style="popularCarousel.getStyle(i)"
            @mouseenter="popularCarousel.focus(i)"
            @click="goArticle(book)"
          >
            <div v-if="i === 0" class="badge crown crownGold" aria-label="1등">
              <svg viewBox="0 0 24 24" class="crownIcon" aria-hidden="true">
                <path
                  fill="currentColor"
                  d="M3 7l4.5 4L12 4l4.5 7L21 7v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7zm2 10h14v-6.2l-2.7 2.1a1 1 0 0 1-1.5-.3L12 8.2 9.2 12.6a1 1 0 0 1-1.5.3L5 10.8V17z"
                />
              </svg>
            </div>
            <div
              v-else-if="i === 1"
              class="badge crown crownSilver"
              aria-label="2등"
            >
              <svg viewBox="0 0 24 24" class="crownIcon" aria-hidden="true">
                <path
                  fill="currentColor"
                  d="M3 7l4.5 4L12 4l4.5 7L21 7v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7zm2 10h14v-6.2l-2.7 2.1a1 1 0 0 1-1.5-.3L12 8.2 9.2 12.6a1 1 0 0 1-1.5.3L5 10.8V17z"
                />
              </svg>
            </div>
            <div
              v-else-if="i === 2"
              class="badge crown crownBronze"
              aria-label="3등"
            >
              <svg viewBox="0 0 24 24" class="crownIcon" aria-hidden="true">
                <path
                  fill="currentColor"
                  d="M3 7l4.5 4L12 4l4.5 7L21 7v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7zm2 10h14v-6.2l-2.7 2.1a1 1 0 0 1-1.5-.3L12 8.2 9.2 12.6a1 1 0 0 1-1.5.3L5 10.8V17z"
                />
              </svg>
            </div>
            <div v-else class="badge rank">#{{ i + 1 }}</div>

            <div
              class="coverFill"
              :style="
                getCoverUrl(book)
                  ? { backgroundImage: `url(${getCoverUrl(book)})` }
                  : {}
              "
            >
              <div class="coverOverlay">
                <div class="bookTitle" :title="getTitle(book)">
                  {{ getTitle(book) }}
                </div>
                <div class="bookAuthor" :title="getAuthor(book)">
                  {{ getAuthor(book) }}
                </div>
              </div>
              <div v-if="!getCoverUrl(book)" class="noCover">No Image</div>
            </div>
          </button>
        </div>

        <!-- ✅ dots active 표시: .value -->
        <div
          v-if="popularBooks.length > 1"
          class="dots"
          aria-label="popular indicator"
        >
          <button
            v-for="(book, di) in popularBooks"
            :key="(getBookId(book) ?? di) + '-p-dot'"
            class="dot"
            type="button"
            :class="{ active: di === popularCarousel.activeIndex.value }"
            @click="popularCarousel.focus(di)"
          />
        </div>
      </div>
    </section>

    <!-- =========================
      추천 TOP5
      - 로그인 전: 블러 + 중앙 문구 + dots 없음 + hover 반응 없음(회전만)
      - 로그인 후: hover/클릭/점 모두 활성화(인기 TOP5 동일 동작)
    ========================= -->
    <section class="section">
      <div class="sectionHeader">
        <h2 class="sectionTitle">추천 도서 TOP5</h2>
        <p class="sectionSub">회원 전용 추천 기능입니다.</p>
      </div>

      <p v-if="recommendedError" class="error">{{ recommendedError }}</p>

      <div
        class="carousel recommendedWrap"
        @mouseenter="isLoggedIn && recommendedCarousel.pause()"
        @mouseleave="isLoggedIn && recommendedCarousel.resume()"
      >
        <div class="carouselStage" :class="{ locked: !isLoggedIn }">
          <div v-if="recommendedLoading" class="loadingLayer">
            <div class="muted">불러오는 중...</div>
          </div>

          <button
            v-for="(book, i) in recommendedBooks"
            :key="(getBookId(book) ?? i) + '-rec'"
            class="carouselCard"
            type="button"
            :style="recommendedCarousel.getStyle(i)"
            @mouseenter="isLoggedIn && recommendedCarousel.focus(i)"
            @click="isLoggedIn && goArticle(book)"
          >
            <div
              class="coverFill"
              :style="
                getCoverUrl(book)
                  ? { backgroundImage: `url(${getCoverUrl(book)})` }
                  : {}
              "
            >
              <div class="coverOverlay">
                <div class="bookTitle" :title="getTitle(book)">
                  {{ getTitle(book) }}
                </div>
                <div class="bookAuthor" :title="getAuthor(book)">
                  {{ getAuthor(book) }}
                </div>
              </div>
              <div v-if="!getCoverUrl(book)" class="noCover">No Image</div>
            </div>
          </button>
        </div>

        <!-- ✅ 로그인 전 문구: stage 밖(블러 영향 없음) -->
        <div
          v-if="!isLoggedIn"
          class="lockedOverlay"
          role="button"
          tabindex="0"
          @click="goLogin"
          @keydown.enter="goLogin"
          @keydown.space.prevent="goLogin"
        >
          <div class="lockedPill">로그인을 하고 추천 도서를 알아보세요!</div>
        </div>

        <!-- ✅ (요구사항 1) 로그인 전에는 dots 없음 -->
        <div
          v-if="isLoggedIn && recommendedBooks.length > 1"
          class="dots"
          aria-label="recommended indicator"
        >
          <button
            v-for="(book, di) in recommendedBooks"
            :key="(getBookId(book) ?? di) + '-r-dot'"
            class="dot"
            type="button"
            :class="{ active: di === recommendedCarousel.activeIndex.value }"
            @click="recommendedCarousel.focus(di)"
          />
        </div>
      </div>
    </section>
  </main>
</template>

<style scoped>
.page {
  max-width: 1100px;
  margin: 0 auto;
  padding: 24px 16px 60px;
  background: #fff;
}

/* HERO */
.hero {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  padding: 18px;
  border: 1px solid #e8e8e8;
  border-radius: 16px;
  background: #ffffff;
}
.heroLeft {
  flex: 1;
}
.heroTitle {
  margin: 0;
  font-size: 34px;
  font-weight: 900;
  letter-spacing: -0.5px;
}
.heroDesc {
  margin: 10px 0 0 0;
  opacity: 0.75;
  line-height: 1.5;
}
.heroActions {
  margin-top: 14px;
  display: flex;
  gap: 10px;
}
.primaryBtn {
  height: 42px;
  padding: 0 14px;
  border-radius: 12px;
  border: 1px solid #111;
  background: #111;
  color: #fff;
  font-weight: 800;
  cursor: pointer;
}
.heroRight {
  width: 260px;
  display: flex;
}
.heroStat {
  width: 100%;
  border-radius: 14px;
  border: 1px solid #e8e8e8;
  background: #fafafa;
  padding: 14px;
}
.heroStatTitle {
  font-weight: 900;
}
.heroStatDesc {
  margin-top: 6px;
  font-size: 13px;
  opacity: 0.7;
}

/* SECTION */
.section {
  margin-top: 18px;
}
.sectionHeader {
  margin-bottom: 12px;
}
.sectionTitle {
  margin: 0;
  font-size: 18px;
  font-weight: 900;
}
.sectionSub {
  margin: 6px 0 0 0;
  font-size: 13px;
  opacity: 0.7;
}

/* CAROUSEL */
.carousel {
  margin-top: 10px;
  position: relative;
}
.carouselStage {
  --shift: min(260px, 28vw);
  --cardW: clamp(190px, 34vw, 290px);
  --cardH: clamp(250px, 46vw, 360px);

  position: relative;
  width: 100%;
  height: var(--cardH);
  border-radius: 18px;
  border: 1px solid #e8e8e8;
  background: #fafafa;
  overflow: hidden;
  perspective: 1100px;
}

/* 로그인 전 추천 블러 */
.carouselStage.locked {
  filter: blur(12px) brightness(0.88) saturate(0.9);
  transform: translateZ(0);
}

.carouselCard {
  position: absolute;
  top: 50%;
  left: 50%;
  width: var(--cardW);
  height: var(--cardH);

  transform-style: preserve-3d;
  transform: translate(-50%, -50%) translateX(var(--tx)) scale(var(--scale))
    rotateY(var(--ry));
  opacity: var(--op);
  z-index: var(--z);

  border: 1px solid #e8e8e8;
  border-radius: 18px;
  background: #fff;
  overflow: hidden;
  padding: 0;
  cursor: pointer;

  transition: transform 650ms cubic-bezier(0.2, 0.8, 0.2, 1), opacity 260ms ease,
    border-color 220ms ease;

  will-change: transform, opacity;
}
.carouselCard:hover {
  border-color: #bdbdbd;
}
.carouselCard:focus {
  outline: none;
}

/* dots */
.dots {
  margin-top: 12px;
  display: flex;
  justify-content: center;
  gap: 8px;
}
.dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  border: 0;
  background: #d5d5d5;
  cursor: pointer;
}
.dot.active {
  background: #111;
}

/* badge */
.badge {
  position: absolute;
  top: 10px;
  left: 10px;
  z-index: 3;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
.rank {
  font-size: 12px;
  font-weight: 900;
  background: #111;
  color: #fff;
  padding: 4px 8px;
  border-radius: 999px;
}

/* crowns */
.crown {
  width: 34px;
  height: 34px;
  border-radius: 999px;
  backdrop-filter: blur(2px);
}
.crownIcon {
  width: 20px;
  height: 20px;
  color: #111;
}
.crownGold {
  background: #d4af37;
}
.crownSilver {
  background: #c0c0c0;
}
.crownBronze {
  background: #cd7f32;
}

/* cover */
.coverFill {
  width: 100%;
  height: 100%;
  background: #f3f3f3;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  position: relative;
}
.coverOverlay {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  padding: 12px;
  z-index: 2;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.65), rgba(0, 0, 0, 0));
  color: #fff;
}
.bookTitle {
  font-weight: 900;
  line-height: 1.25;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.bookAuthor {
  margin-top: 6px;
  font-size: 13px;
  opacity: 0.85;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.noCover {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.7;
  z-index: 1;
  color: #333;
}

/* skeleton */
.skeletonCard {
  background: #f1f1f1;
  border: 1px solid #e8e8e8;
}

/* recommended overlay (로그인 전 문구) */
.recommendedWrap {
  position: relative;
}
.lockedOverlay {
  position: absolute;
  inset: 0;
  z-index: 50;
  display: flex;
  align-items: center;
  justify-content: center;
}
.lockedPill {
  background: rgba(17, 17, 17, 0.92);
  color: #fff;
  padding: 12px 16px;
  border-radius: 999px;
  font-weight: 900;
  cursor: pointer;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.15);
}

/* loading layer */
.loadingLayer {
  position: absolute;
  inset: 0;
  z-index: 40;
  display: flex;
  align-items: center;
  justify-content: center;
}

.muted {
  opacity: 0.7;
  text-align: center;
  margin-top: 16px;
}
.error {
  color: #ff6b6b;
}

@media (max-width: 600px) {
  .hero {
    flex-direction: column;
  }
  .heroRight {
    width: 100%;
  }
  .carouselStage {
    --shift: min(190px, 34vw);
  }
}
</style>
