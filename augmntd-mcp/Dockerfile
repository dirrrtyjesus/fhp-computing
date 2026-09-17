# ---------------------------------------------------------
# Stage 1: Build & Prune
# ---------------------------------------------------------
FROM node:22-alpine AS builder
WORKDIR /app

RUN corepack enable && corepack prepare pnpm@latest --activate

COPY package.json pnpm-workspace.yaml* pnpm-lock.yaml* package-lock.json* ./
RUN if [ -f pnpm-lock.yaml ]; then \
      pnpm install --frozen-lockfile; \
    else \
      pnpm install; \
    fi

COPY tsconfig.json ./
COPY src/ ./src/
RUN pnpm build

# ---------------------------------------------------------
# Stage 2: Production Runtime
# ---------------------------------------------------------
FROM node:22-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production

# 1. Install production deps as root
COPY package.json pnpm-workspace.yaml* pnpm-lock.yaml* package-lock.json* ./
RUN corepack enable && corepack prepare pnpm@latest --activate && \
    if [ -f pnpm-lock.yaml ]; then \
      pnpm install --prod --frozen-lockfile; \
    else \
      pnpm install --prod; \
    fi

COPY --from=builder /app/dist ./dist

# 2. Switch to non-root user AFTER root installations
USER node

# Cloud Run defaults to PORT 8080
ENV PORT=8080
EXPOSE 8080

CMD ["node", "dist/server.js"]
