<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import api from "@/api/axios";

const router = useRouter();

const popularBooks = ref([]);
const isLoading = ref(false);
const errorMessage = ref("");

const activeIndex = ref(0); // 현재 "가운데(2번째 자리)"에 오는 책의 인덱스
const isPaused = ref(false);

const rotationTimerId = ref(null);
const rotationIntervalMs = 2700;

function stopAutoRotate() {
  if (rotationTimerId.value !== null) {
    clearInterval(rotationTimerId.value);
    rotationTimerId.value = null;
  }
}

function startAutoRotate() {
  stopAutoRotate();

  rotationTimerId.value = setInterval(() => {
    const booksLength = popularBooks.value.length;
    if (booksLength <= 1) {
      return;
    }

    if (isPaused.value) {
      return;
    }

    const nextIndex = activeIndex.value + 1;
    if (nextIndex >= booksLength) {
      activeIndex.value = 0;
      return;
    }

    activeIndex.value = nextIndex;
  }, rotationIntervalMs);
}

function pauseAutoRotate() {
  isPaused.value = true;
}

function resumeAutoRotate() {
  isPaused.value = false;
}

function focusBook(bookIndex) {
  const booksLength = popularBooks.value.length;
  if (booksLength <= 0) {
    return;
  }

  if (bookIndex === activeIndex.value) {
    return;
  }

  activeIndex.value = bookIndex;
}

function getBookId(book) {
  const bookId = book?.id ?? book?.pk ?? book?.book_id ?? book?.bookId;
  if (bookId === undefined || bookId === null) {
    throw new Error(
      "Book id가 없습니다. (id/pk/book_id/bookId 중 하나가 필요)"
    );
  }
  return bookId;
}

async function goBookDetail(book) {
  const bookId = getBookId(book);

  // 1순위: name 기반 라우팅
  try {
    await router.push({ name: "article", params: { id: bookId } });
    return;
  } catch (error) {
    // 2순위: path 기반 라우팅(혹시 name이 다르거나 params 매칭이 안될 때)
    await router.push(`/article/${bookId}`);
  }
}

function getDelta(bookIndex) {
  const booksLength = popularBooks.value.length;
  if (booksLength <= 0) {
    return 0;
  }

  let delta = (bookIndex - activeIndex.value) % booksLength;
  if (delta < 0) {
    delta += booksLength;
  }
  return delta;
}

/**
 * delta 기준:
 * 0 = 가운데(큰 카드)
 * 1 = 오른쪽(작은 카드)
 * length-1 = 왼쪽(작은 카드)
 * 나머지 = 숨김
 */
function getCarouselStyle(bookIndex) {
  const booksLength = popularBooks.value.length;

  const styleObject = {
    "--tx": "0px",
    "--scale": "0.7",
    "--op": "0",
    "--ry": "0deg",
    zIndex: 0,
    pointerEvents: "none",
  };

  if (booksLength <= 0) {
    return styleObject;
  }

  const delta = getDelta(bookIndex);

  if (delta === 0) {
    styleObject["--tx"] = "0px";
    styleObject["--scale"] = "1.08";
    styleObject["--op"] = "1";
    styleObject["--ry"] = "0deg";
    styleObject.zIndex = 30;
    styleObject.pointerEvents = "auto";
    return styleObject;
  }

  if (delta === 1) {
    styleObject["--tx"] = "var(--shift)";
    styleObject["--scale"] = "0.86";
    styleObject["--op"] = "0.94";
    styleObject["--ry"] = "-10deg";
    styleObject.zIndex = 20;
    styleObject.pointerEvents = "auto";
    return styleObject;
  }

  if (delta === booksLength - 1) {
    styleObject["--tx"] = "calc(var(--shift) * -1)";
    styleObject["--scale"] = "0.86";
    styleObject["--op"] = "0.94";
    styleObject["--ry"] = "10deg";
    styleObject.zIndex = 20;
    styleObject.pointerEvents = "auto";
    return styleObject;
  }

  return styleObject;
}

async function fetchPopularTop5() {
  isLoading.value = true;
  errorMessage.value = "";

  try {
    const response = await api.get("/articles/books/popular/");
    const data = response.data;

    const list = Array.isArray(data) ? data : data?.results ?? [];

    // ✅ 여기: 응답 구조가 어떻든 "상세 이동용 id"를 _id에 고정
    popularBooks.value = list.map((rawBook) => {
      const extractedId =
        rawBook?.id ??
        rawBook?.pk ??
        rawBook?.book_id ??
        rawBook?.bookId ??
        rawBook?.book_pk ??
        rawBook?.bookPk ??
        // ✅ rawBook.book 이 숫자/문자(=id)로 오는 케이스 대응
        (typeof rawBook?.book === "number" || typeof rawBook?.book === "string"
          ? rawBook.book
          : undefined) ??
        // ✅ rawBook.book 이 객체로 오는 케이스
        rawBook?.book?.id ??
        rawBook?.book?.pk;

      return {
        ...rawBook,
        _id: extractedId, // <- 무조건 이걸로 상세 이동
        title: rawBook?.title ?? rawBook?.book?.title ?? "(제목 없음)",
        author: rawBook?.author ?? rawBook?.book?.author ?? "",
        cover:
          rawBook?.cover ??
          rawBook?.cover_img ??
          rawBook?.coverImage ??
          rawBook?.image ??
          rawBook?.thumbnail ??
          rawBook?.book?.cover ??
          rawBook?.book?.cover_img ??
          "",
      };
    });

    // 디버그(첫 데이터 구조 확인용)
    console.log("popularBooks sample:", popularBooks.value[0]);

    activeIndex.value = 0;
    startAutoRotate();
  } catch (error) {
    popularBooks.value = [];
    errorMessage.value = "인기 도서를 불러오지 못했습니다.";
    stopAutoRotate();
  } finally {
    isLoading.value = false;
  }
}

function goDetail(book) {
  const bookId = book?._id;

  if (bookId === undefined || bookId === null || bookId === "") {
    console.log("CLICKED BOOK:", book);
    alert(
      "이 책 데이터에서 id(_id)를 못 찾았습니다. 콘솔의 CLICKED BOOK 확인하세요."
    );
    return;
  }

  router.push({ name: "article", params: { id: String(bookId) } });
}

function goList() {
  router.push("/list");
}

onMounted(fetchPopularTop5);

onBeforeUnmount(() => {
  stopAutoRotate();
});

const hasBooks = computed(() => popularBooks.value.length > 0);
</script>

<template>
  <main class="page">
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

    <section class="section">
      <div class="sectionHeader">
        <h2 class="sectionTitle">인기 도서 TOP5</h2>
        <p class="sectionSub">인기있는 도서를 확인하세요!</p>
      </div>

      <p v-if="errorMessage" class="error">{{ errorMessage }}</p>

      <!-- 로딩: 3개 스켈레톤 -->
      <div v-if="isLoading" class="carousel">
        <div class="carouselStage">
          <div
            class="carouselCard skeletonCard"
            style="
              --tx: calc(var(--shift) * -1);
              --scale: 0.86;
              --op: 0.94;
              --ry: 10deg;
            "
          ></div>
          <div
            class="carouselCard skeletonCard"
            style="--tx: 0px; --scale: 1.08; --op: 1; --ry: 0deg"
          ></div>
          <div
            class="carouselCard skeletonCard"
            style="--tx: var(--shift); --scale: 0.86; --op: 0.94; --ry: -10deg"
          ></div>
        </div>
      </div>

      <div
        v-else
        class="carousel"
        @mouseenter="pauseAutoRotate"
        @mouseleave="resumeAutoRotate"
      >
        <div v-if="hasBooks" class="carouselStage">
          <button
            v-for="(book, bookIndex) in popularBooks"
            :key="book._id ?? bookIndex"
            class="carouselCard"
            type="button"
            :style="getCarouselStyle(bookIndex)"
            @mouseenter="focusBook(bookIndex)"
            @click="goDetail(book)"
          >
            <!-- 왕관/등수: '전체 TOP5 순위' 기준 -->
            <div
              v-if="bookIndex === 0"
              class="badge crown crownGold"
              aria-label="1등"
            >
              <svg viewBox="0 0 24 24" class="crownIcon" aria-hidden="true">
                <path
                  fill="currentColor"
                  d="M3 7l4.5 4L12 4l4.5 7L21 7v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7zm2 10h14v-6.2l-2.7 2.1a1 1 0 0 1-1.5-.3L12 8.2 9.2 12.6a1 1 0 0 1-1.5.3L5 10.8V17z"
                />
              </svg>
            </div>

            <div
              v-else-if="bookIndex === 1"
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
              v-else-if="bookIndex === 2"
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

            <div v-else class="badge rank">#{{ bookIndex + 1 }}</div>

            <!-- 표지로 꽉 채우기 -->
            <div
              class="coverFill"
              :style="
                book.cover ? { backgroundImage: `url(${book.cover})` } : {}
              "
            >
              <div class="coverOverlay">
                <div class="bookTitle" :title="book.title">
                  {{ book.title }}
                </div>
                <div class="bookAuthor" :title="book.author">
                  {{ book.author }}
                </div>
              </div>

              <div v-if="!book.cover" class="noCover">No Image</div>
            </div>
          </button>
        </div>

        <p v-else class="muted">인기 도서 데이터가 없습니다.</p>

        <!-- 점 인디케이터 (클릭하면 해당 책을 가운데로) -->
        <div
          v-if="popularBooks.length > 1"
          class="dots"
          aria-label="carousel indicator"
        >
          <button
            v-for="(book, dotIndex) in popularBooks"
            :key="book.id + '-dot'"
            class="dot"
            type="button"
            :class="{ active: dotIndex === activeIndex }"
            @click="focusBook(dotIndex)"
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

  display: block;
  perspective: 1100px;
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
  background: rgba(0, 0, 0, 0.45);
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

/* cover fill */
.coverFill {
  width: 100%;
  height: 100%;
  background: #f3f3f3;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  position: relative;
}

/* title overlay */
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

/* misc */
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
