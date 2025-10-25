# Beanflow Design System
**Version**: 1.1  
**Created**: 2025-01-29  
**Updated**: 2025-09-15  
**Based on**: Material Design 3 (Material You)

---

## 🎨 Brand Identity

### Brand Mission
AI-powered automated bookkeeping for Canadian small businesses and accounting firms.

### Design Philosophy
- **Professional yet approachable**: Clean, modern design that builds trust
- **AI-focused**: Emphasize intelligent automation and effortless experience  
- **Canadian-first**: Localized for Canadian business needs and culture
- **Accessibility**: Inclusive design for all users

---

## 🌈 Color System

Our color system is based on Material Design 3, providing semantic meaning and consistent visual hierarchy.

### Primary Colors
Used for primary actions, key UI elements, and brand expression.

```css
primary: {
  50:  '#e8f4fd',   /* Lightest - backgrounds, subtle accents */
  100: '#d1e9fb',   /* Light - hover states */
  200: '#a3d3f7',   /* Light medium - disabled states */
  300: '#75bdf3',   /* Medium light - secondary elements */
  400: '#47a7ef',   /* Medium - supporting elements */
  500: '#1976d2',   /* Main - primary buttons, links, brand */
  600: '#1565c0',   /* Medium dark - hover states */
  700: '#0d47a1',   /* Dark - pressed states */
  800: '#0a3d8a',   /* Darker - high contrast text */
  900: '#073373'    /* Darkest - maximum contrast */
}
```

**Primary Use Cases:**
- ✅ Primary buttons and CTAs
- ✅ Navigation active states  
- ✅ Brand logo and key elements
- ✅ Progress indicators
- ✅ Important notifications

### Secondary Colors
Used for secondary actions and complementary UI elements.

```css
secondary: {
  50:  '#f3e5f5',   /* Lightest */
  100: '#e1bee7',   /* Light */
  200: '#ce93d8',   /* Light medium */
  300: '#ba68c8',   /* Medium light */
  400: '#ab47bc',   /* Medium */
  500: '#9c27b0',   /* Main - secondary brand color */
  600: '#8e24aa',   /* Medium dark */
  700: '#7b1fa2',   /* Dark */
  800: '#6a1b9a',   /* Darker */
  900: '#4a148c'    /* Darkest */
}
```

**Secondary Use Cases:**
- ✅ Secondary buttons
- ✅ Accent elements
- ✅ Feature highlights
- ✅ AI/automation indicators

### Tertiary Colors
Used for success states, confirmations, and positive feedback.

```css
tertiary: {
  50:  '#e0f2f1',   /* Lightest */
  100: '#b2dfdb',   /* Light */
  200: '#80cbc4',   /* Light medium */
  300: '#4db6ac',   /* Medium light */
  400: '#26a69a',   /* Medium */
  500: '#009688',   /* Main - success, confirmation */
  600: '#00897b',   /* Medium dark */
  700: '#00796b',   /* Dark */
  800: '#00695c',   /* Darker */
  900: '#004d40'    /* Darkest */
}
```

**Tertiary Use Cases:**
- ✅ Success messages and states
- ✅ Completed actions
- ✅ Positive metrics and KPIs
- ✅ Check marks and confirmations

### Surface Colors
Used for backgrounds, cards, and container elements.

```css
surface: {
  50:  '#fefefe',   /* Lightest - main backgrounds */
  100: '#fdfdfd',   /* Very light */
  200: '#f8f9fa',   /* Light - card backgrounds */
  300: '#f1f3f4',   /* Light medium - hover states */
  400: '#e8eaed',   /* Medium - borders, dividers */
  500: '#dadce0',   /* Medium dark - inactive elements */
  600: '#bdc1c6',   /* Dark - secondary text */
  700: '#9aa0a6',   /* Darker - supporting text */
  800: '#5f6368',   /* Very dark - primary text */
  900: '#202124'    /* Darkest - headings, emphasis */
}
```

### Error Colors
Used for error states, warnings, and critical feedback.

```css
error: {
  50:  '#ffebee',   /* Lightest */
  100: '#ffcdd2',   /* Light */
  200: '#ef9a9a',   /* Light medium */
  300: '#e57373',   /* Medium light */
  400: '#ef5350',   /* Medium */
  500: '#f44336',   /* Main - errors, warnings */
  600: '#e53935',   /* Medium dark */
  700: '#d32f2f',   /* Dark */
  800: '#c62828',   /* Darker */
  900: '#b71c1c'    /* Darkest */
}
```

### Canadian Theme Colors
Special colors for Canadian localization and branding.

```css
canadian: {
  red: '#ff0000',      /* Canadian flag red */
  maple: '#d2691e',    /* Maple leaf brown/orange */
  winter: '#e6f3ff',   /* Light winter blue */
  forest: '#228b22'    /* Canadian forest green */
}
```

---

## 📝 Typography System

### Font Family
**Primary**: Roboto (Google Fonts)  
**Fallback**: system-ui, sans-serif

```css
font-family: 'Roboto', system-ui, sans-serif;
```

### Type Scale
Based on Material Design 3 typography scale.

#### Display Large
```css
font-size: 57px;
line-height: 64px;
font-weight: 400;
letter-spacing: -0.25px;
```
**Use Cases:** Hero headlines, major page titles

#### Display Medium  
```css
font-size: 45px;
line-height: 52px;
font-weight: 400;
letter-spacing: 0;
```
**Use Cases:** Section titles, important headings

#### Display Small
```css
font-size: 36px;
line-height: 44px;
font-weight: 400;
letter-spacing: 0;
```
**Use Cases:** Page headings, card titles

#### Headline Large
```css
font-size: 32px;
line-height: 40px;
font-weight: 400;
letter-spacing: 0;
```
**Use Cases:** Section headings, feature titles

#### Headline Medium
```css
font-size: 28px;
line-height: 36px;
font-weight: 400;
letter-spacing: 0;
```
**Use Cases:** Subsection headings

#### Headline Small
```css
font-size: 24px;
line-height: 32px;
font-weight: 400;
letter-spacing: 0;
```
**Use Cases:** Card headings, dialog titles

#### Title Large
```css
font-size: 22px;
line-height: 28px;
font-weight: 500;
letter-spacing: 0;
```
**Use Cases:** Prominent text, app bar titles

#### Title Medium
```css
font-size: 16px;
line-height: 24px;
font-weight: 500;
letter-spacing: 0.15px;
```
**Use Cases:** Medium emphasis text

#### Title Small
```css
font-size: 14px;
line-height: 20px;
font-weight: 500;
letter-spacing: 0.1px;
```
**Use Cases:** Small headings, tabs

#### Body Large
```css
font-size: 16px;
line-height: 24px;
font-weight: 400;
letter-spacing: 0.5px;
```
**Use Cases:** Main body text, descriptions

#### Body Medium
```css
font-size: 14px;
line-height: 20px;
font-weight: 400;
letter-spacing: 0.25px;
```
**Use Cases:** Supporting text, captions

#### Body Small
```css
font-size: 12px;
line-height: 16px;
font-weight: 400;
letter-spacing: 0.4px;
```
**Use Cases:** Helper text, metadata

#### Label Large
```css
font-size: 14px;
line-height: 20px;
font-weight: 500;
letter-spacing: 0.1px;
```
**Use Cases:** Button text, form labels

#### Label Medium
```css
font-size: 12px;
line-height: 16px;
font-weight: 500;
letter-spacing: 0.5px;
```
**Use Cases:** Tab labels, chip labels

#### Label Small
```css
font-size: 11px;
line-height: 16px;
font-weight: 500;
letter-spacing: 0.5px;
```
**Use Cases:** Small labels, badges

---

## 🔲 Border Radius System

Consistent rounded corners throughout the interface.

```css
border-radius: {
  none: '0',        /* Sharp corners - technical/data elements */
  sm:   '4px',      /* Subtle - small elements, inputs */
  md:   '8px',      /* Standard - most UI elements */
  lg:   '12px',     /* Medium - cards, containers */
  xl:   '16px',     /* Large - prominent cards */
  2xl:  '20px',     /* Extra large - hero cards */
  3xl:  '28px',     /* Maximum - buttons, pills */
  full: '9999px'    /* Circular - avatars, badges */
}
```

**Usage Guidelines:**
- **Buttons**: 3xl (28px) for a modern, friendly appearance
- **Cards**: lg-2xl (12px-20px) based on size and importance
- **Inputs**: sm-md (4px-8px) for professional look
- **Images**: md-xl (8px-16px) for visual harmony

---

## 🌫️ Shadow System

Material Design 3 elevation system for depth and hierarchy.

### Shadow Levels

#### Level 1 - Subtle
```css
box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.3), 0 4px 8px 3px rgba(0, 0, 0, 0.15);
```
**Use Cases:** Slight separation, hover states

#### Level 2 - Low  
```css
box-shadow: 0 2px 6px 2px rgba(0, 0, 0, 0.15), 0 8px 24px 4px rgba(0, 0, 0, 0.3);
```
**Use Cases:** Cards, containers

#### Level 3 - Medium
```css
box-shadow: 0 4px 8px 3px rgba(0, 0, 0, 0.15), 0 8px 10px 1px rgba(0, 0, 0, 0.3);
```
**Use Cases:** Prominent cards, buttons

#### Level 4 - High
```css
box-shadow: 0 6px 10px 4px rgba(0, 0, 0, 0.15), 0 24px 38px 3px rgba(0, 0, 0, 0.3);
```
**Use Cases:** Modals, dropdowns

#### Level 5 - Maximum
```css
box-shadow: 0 8px 12px 6px rgba(0, 0, 0, 0.15), 0 40px 64px 12px rgba(0, 0, 0, 0.3);
```
**Use Cases:** Full-screen overlays, major dialogs

---

## 📏 Spacing System

Based on 8px grid system for consistent spacing and alignment.

### Base Unit: 8px

```css
spacing: {
  0:   '0',         /* No spacing */
  1:   '4px',       /* 0.5 × base */
  2:   '8px',       /* 1 × base */
  3:   '12px',      /* 1.5 × base */
  4:   '16px',      /* 2 × base */
  5:   '20px',      /* 2.5 × base */
  6:   '24px',      /* 3 × base */
  8:   '32px',      /* 4 × base */
  10:  '40px',      /* 5 × base */
  12:  '48px',      /* 6 × base */
  16:  '64px',      /* 8 × base */
  20:  '80px',      /* 10 × base */
  24:  '96px',      /* 12 × base */
  32:  '128px',     /* 16 × base */
  40:  '160px',     /* 20 × base */
  48:  '192px',     /* 24 × base */
  56:  '224px',     /* 28 × base */
  64:  '256px'      /* 32 × base */
}
```

### Usage Guidelines
- **Micro spacing**: 4px-8px - Between related elements
- **Component spacing**: 12px-24px - Between UI components  
- **Section spacing**: 32px-64px - Between page sections
- **Layout spacing**: 80px+ - Between major layout areas

---

## 🎬 Animation System

Consistent motion design for smooth, purposeful interactions.

### Easing Functions

#### Standard Easing
```css
transition: cubic-bezier(0.4, 0.0, 0.2, 1);
```
**Use Cases:** Most UI transitions, hover states

#### Decelerate Easing
```css
transition: cubic-bezier(0.0, 0.0, 0.2, 1);
```
**Use Cases:** Elements entering the screen

#### Accelerate Easing  
```css
transition: cubic-bezier(0.4, 0.0, 1, 1);
```
**Use Cases:** Elements exiting the screen

### Duration Guidelines

```css
durations: {
  fast:     '150ms',    /* Micro-interactions, hover */
  medium:   '300ms',    /* Standard transitions */
  slow:     '500ms',    /* Complex animations */
  extended: '800ms'     /* Page transitions */
}
```

### Key Animations

#### Float Animation
```css
@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-16px); }
}
animation: float 8s ease-in-out infinite;
```

#### Ripple Effect
```css
@keyframes ripple {
  0% { transform: scale(0); opacity: 1; }
  100% { transform: scale(4); opacity: 0; }
}
```

#### Fade In Up
```css
@keyframes fadeInUp {
  from { 
    opacity: 0; 
    transform: translateY(20px); 
  }
  to { 
    opacity: 1; 
    transform: translateY(0); 
  }
}
```

---

## 🧩 Component Library

### Buttons

#### Primary Button
```css
.btn-primary {
  background: linear-gradient(135deg, #1976d2, #9c27b0);
  color: white;
  padding: 16px 32px;
  border-radius: 28px;
  font-weight: 500;
  box-shadow: 0 4px 8px 3px rgba(0, 0, 0, 0.15);
  transition: all 0.3s cubic-bezier(0.4, 0.0, 0.2, 1);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 10px 4px rgba(0, 0, 0, 0.15);
}
```

#### Secondary Button
```css
.btn-secondary {
  background: transparent;
  color: #1976d2;
  border: 2px solid #1976d2;
  padding: 14px 30px;
  border-radius: 28px;
  font-weight: 500;
  transition: all 0.3s cubic-bezier(0.4, 0.0, 0.2, 1);
}

.btn-secondary:hover {
  background: #e8f4fd;
  transform: translateY(-2px);
}
```

### Cards

#### Elevated Card
```css
.card-elevated {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 32px;
  box-shadow: 0 4px 8px 3px rgba(0, 0, 0, 0.15);
  transition: all 0.3s cubic-bezier(0.4, 0.0, 0.2, 1);
}

.card-elevated:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 12px 6px rgba(0, 0, 0, 0.15);
}
```

#### Feature Card
```css
.card-feature {
  background: white;
  border-radius: 24px;
  padding: 40px;
  box-shadow: 0 2px 6px 2px rgba(0, 0, 0, 0.15);
  transition: all 0.3s cubic-bezier(0.4, 0.0, 0.2, 1);
}

.card-feature:hover {
  transform: translateY(-4px);
  box-shadow: 0 6px 10px 4px rgba(0, 0, 0, 0.15);
}
```

### Navigation

#### Navigation Bar
```css
.navbar {
  position: fixed;
  top: 0;
  width: 100%;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid #e8eaed;
  z-index: 1000;
}
```

### Icons

#### Icon Containers
```css
.icon-container {
  width: 64px;
  height: 64px;
  border-radius: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.icon-primary {
  background: #e8f4fd;
  color: #1976d2;
}

.icon-secondary {
  background: #f3e5f5;
  color: #9c27b0;
}

.icon-tertiary {
  background: #e0f2f1;
  color: #009688;
}
```

---

## 📱 Responsive Design

### Breakpoints

```css
breakpoints: {
  sm:  '640px',    /* Small devices (phones) */
  md:  '768px',    /* Medium devices (tablets) */
  lg:  '1024px',   /* Large devices (laptops) */
  xl:  '1280px',   /* Extra large devices (desktops) */
  2xl: '1536px'    /* 2X large devices (large desktops) */
}
```

### Container Sizes

```css
containers: {
  sm:  '640px',    /* Content width for small screens */
  md:  '768px',    /* Content width for medium screens */
  lg:  '1024px',   /* Content width for large screens */
  xl:  '1200px',   /* Standard content width */
  2xl: '1400px'    /* Wide content width */
}
```

### Responsive Typography

#### Mobile First Approach
```css
/* Mobile (default) */
.hero-title {
  font-size: 48px;
  line-height: 1.2;
}

/* Tablet and up */
@media (min-width: 768px) {
  .hero-title {
    font-size: 56px;
  }
}

/* Desktop and up */
@media (min-width: 1024px) {
  .hero-title {
    font-size: 64px;
  }
}
```

---

## 🎯 Brand-Specific Elements

### Gradients

#### Primary Brand Gradient
```css
background: linear-gradient(135deg, #1976d2, #9c27b0, #009688);
```
**Use Cases:** Hero sections, premium features, brand highlights

#### Subtle Background Gradient
```css
background: linear-gradient(135deg, #e8f4fd, #f3e5f5);
```
**Use Cases:** Section backgrounds, card overlays

### Canadian Localization

#### Maple Leaf Icon
Use Font Awesome `fas fa-maple-leaf` or custom SVG

#### Canadian Flag Colors
```css
.canadian-accent {
  border-left: 4px solid #ff0000;
}
```

#### Bilingual Typography
Ensure sufficient line-height for French text with accents:
```css
line-height: 1.6; /* Increased for French compatibility */
```

---

## ✅ Accessibility Guidelines

### Color Contrast
- **Normal text**: Minimum 4.5:1 contrast ratio
- **Large text**: Minimum 3:1 contrast ratio
- **UI elements**: Minimum 3:1 contrast ratio

### Focus States
```css
.focusable:focus {
  outline: 2px solid #1976d2;
  outline-offset: 2px;
}
```

### Interactive Elements
- **Minimum touch target**: 44px × 44px
- **Keyboard navigation**: All interactive elements must be keyboard accessible
- **Screen reader support**: Proper ARIA labels and semantic HTML

---

## 📐 Layout Principles

### Grid System
Based on 12-column grid with flexible gutters:

```css
.grid-container {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 24px;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
}
```

### Vertical Rhythm
Maintain consistent vertical spacing using multiples of 8px:

```css
.section {
  padding: 80px 0; /* 10 × 8px */
}

.section-header {
  margin-bottom: 64px; /* 8 × 8px */
}

.content-block {
  margin-bottom: 32px; /* 4 × 8px */
}
```

---

## 🎨 Implementation Guidelines

### CSS Variables
Define design tokens as CSS custom properties:

```css
:root {
  /* Colors */
  --color-primary: #1976d2;
  --color-secondary: #9c27b0;
  --color-tertiary: #009688;
  
  /* Typography */
  --font-family-primary: 'Roboto', system-ui, sans-serif;
  --font-size-hero: clamp(48px, 8vw, 64px);
  
  /* Spacing */
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 32px;
  --spacing-xl: 64px;
  
  /* Border Radius */
  --radius-sm: 8px;
  --radius-md: 16px;
  --radius-lg: 24px;
  --radius-xl: 32px;
  
  /* Shadows */
  --shadow-sm: 0 2px 6px 2px rgba(0, 0, 0, 0.15);
  --shadow-md: 0 4px 8px 3px rgba(0, 0, 0, 0.15);
  --shadow-lg: 0 8px 12px 6px rgba(0, 0, 0, 0.15);
  
  /* Transitions */
  --transition-fast: 150ms cubic-bezier(0.4, 0.0, 0.2, 1);
  --transition-standard: 300ms cubic-bezier(0.4, 0.0, 0.2, 1);
}
```

### Utility Classes
Create reusable utility classes for common patterns:

```css
/* Spacing Utilities */
.p-xs { padding: var(--spacing-xs); }
.p-sm { padding: var(--spacing-sm); }
.p-md { padding: var(--spacing-md); }
.p-lg { padding: var(--spacing-lg); }

.m-xs { margin: var(--spacing-xs); }
.m-sm { margin: var(--spacing-sm); }
.m-md { margin: var(--spacing-md); }
.m-lg { margin: var(--spacing-lg); }

/* Text Utilities */
.text-primary { color: var(--color-primary); }
.text-secondary { color: var(--color-secondary); }
.text-muted { color: var(--surface-700); }

/* Background Utilities */
.bg-gradient-primary {
  background: linear-gradient(135deg, var(--color-primary), var(--color-secondary));
}

.bg-surface { background-color: var(--surface-100); }
```

---

## 📋 Design Checklist

### Before Creating New Components
- [ ] Does this component follow the established color system?
- [ ] Are the border radius values consistent with the design system?
- [ ] Does the component use appropriate shadow levels?
- [ ] Are spacing values based on the 8px grid system?
- [ ] Does the typography follow the established scale?
- [ ] Is the component accessible (contrast, focus states, keyboard navigation)?
- [ ] Does it work on mobile devices?
- [ ] Are hover and active states defined?
- [ ] Does it include proper loading and error states?

### Quality Assurance
- [ ] Test on multiple screen sizes
- [ ] Verify color contrast ratios
- [ ] Test with keyboard navigation
- [ ] Validate with screen readers
- [ ] Check performance impact
- [ ] Ensure consistent spacing
- [ ] Verify brand alignment

---

## 🔄 Maintenance and Updates

### Versioning
- **Major Version**: Breaking changes to design tokens or component structure
- **Minor Version**: New components or non-breaking enhancements  
- **Patch Version**: Bug fixes and small adjustments

### Change Process
1. **Proposal**: Document the change with rationale
2. **Review**: Design team evaluation and feedback
3. **Implementation**: Update design system and components
4. **Documentation**: Update this guide and component library
5. **Communication**: Notify all team members of changes

### Regular Reviews
- **Monthly**: Review usage analytics and feedback
- **Quarterly**: Assess design system effectiveness
- **Annually**: Major version planning and roadmap updates

---

## 📞 Contact and Support

For questions about this design system:
- **Design Team**: [design@beanflow.ca]
- **Documentation**: This guide and component library
- **Updates**: Check version history in git commits

Remember: Consistency is key. When in doubt, refer to this guide or ask the design team.

---

*This design system is a living document. It evolves with our product and user needs while maintaining consistency and quality.*


---

## 🧭 Workspace Layout (App v2-current)

The application workspace uses a 4-column responsive grid with a collapsible left sidebar, a narrow middle utility bar, and a right-side AI Assistant panel.

### Desktop Grid
```css
/* Default: sidebar 280, content 1fr, middle 60, AI 500 */
.desktop-layout {
  display: grid;
  grid-template-columns: 280px 1fr 60px 500px;
  min-height: 100dvh;
}

/* Collapsed sidebar */
.desktop-layout.sidebar-collapsed {
  grid-template-columns: 64px 1fr 60px 500px;
}

/* AI hidden */
.desktop-layout.ai-hidden {
  grid-template-columns: 280px 1fr 60px;
}

/* Collapsed + AI hidden */
.desktop-layout.sidebar-collapsed.ai-hidden {
  grid-template-columns: 64px 1fr 60px;
}
```

### Responsive Behavior
```css
/* <= 1200px: hide left sidebar + middle bar; main + AI (if visible) */
@media (max-width: 1200px) {
  .desktop-layout { grid-template-columns: 1fr; }
  .desktop-layout:not(.ai-hidden) { grid-template-columns: 1fr 400px !important; }
}

/* <= 1024px: AI 优先视图 (与 Tailwind lg 断点保持一致) */
@media (max-width: 1024px) {
  .desktop-layout { grid-template-columns: 1fr !important; }
  /* AI 可见：仅显示 AI 面板（全宽） */
  .desktop-layout:not(.ai-hidden) .main-content { display: none !important; }
  .desktop-layout:not(.ai-hidden) .ai-panel { display: block !important; width: 100% !important; grid-column: 1 / -1; }
  /* AI 隐藏：仅显示主内容 */
  .desktop-layout.ai-hidden .ai-panel { display: none !important; }
  .desktop-layout.ai-hidden .main-content { display: block !important; grid-column: 1 / -1; }
}
```

### Scroll & Overflow
- 主内容区与 AI 面板各自独立滚动，使用 `height: 100dvh; overflow-y: auto;`。
- 移动端固定底部输入（AI 面板）须预留底部内边距，避免被遮挡。

---

## 📊 Transactions List（Data Table Pattern）

适用于交易流水列表（v2-current）：按月分组、虚拟滚动、可展开详情、附件与复核状态。参考 Material Design 3 的 Data tables 原则，并与现有实现一致。

### 适用范围
- 组件：`VirtualTransactionList`、`TransactionItem`、`MonthHeader`
- 场景：交易流水浏览、筛选、分页加载、复核、附件预览/下载

### 信息架构与列（IA）
- 列与字段：
  - Date（日期，等宽字体，固定宽度）
  - Description/Narration（叙述/摘要，单行截断）
  - Accounts（账户：Primary → Secondary +N）
  - Amount（金额，右对齐）
  - Currency（币种，右对齐，三字母大写）
  - Review Status（复核状态：Reviewed/Needs Review）
  - Attachment（附件：回形针图标）
- 对齐：文本左对齐；数值右对齐；日期等宽；币种大写（可增加微字距）
- 宽度建议：
  - Date：88–96px 固定（等宽便于纵向比对）
  - Description：弹性伸展，单行省略号
  - Accounts：≥200px，容纳箭头与“+N more”
  - Amount：120–140px（右对齐）
  - Currency：56–72px（右对齐）
- 金额着色（与实现对齐）：
  - 过滤某账户时，显示实际符号：正数 inflow 用成功色；负数 outflow 用错误色
  - 未过滤时显示绝对值，用主文本色

### 尺寸与密度
- 行高：默认 60px；紧凑 48px；舒适 72px（触控优先）
- 单元格内边距：左右 16px，上下 12px
- 操作命中：附件/复核/展开 ≥ 44×44px

### 分组与表头
- 按月分组：`MonthHeader` 粘性（sticky top: 0），高度 60px
- 右侧可选展示该月净额：>0 使用成功色标注“Income”，<0 使用错误色标注“Expense”
- 头部徽记展示该月条数（浅色胶囊）

### 交互与状态
- Hover：行背景 `--color-surface-50`；可点击图标提高对比
- Focus：统一 `outline: 2px solid var(--color-primary-500); outline-offset: 2px;`
- Expand：右侧箭头点击/键盘展开详情；展开行可加淡蓝描边（现有实现）
- Review：`*` Reviewed（绿色胶囊）、`!` Needs Review（黄色胶囊），点击切换
- Attachment：回形针图标点击新开页；后续可升级为 Modal 预览
- 空/加载/错误：
  - 空：图标 + 主文案 + 次要说明
  - 加载：行骨架（建议补充）或列表内轻量加载指示
  - 错误：红色轻量告警卡片

### 排序与筛选
- 排序（Table 形态）：默认日期倒序；可切换 Amount/Payee 升降序
- 筛选：保留顶部的 `AccountFilter`、`ReviewStatusFilter`、`PageSizeSelector`；过滤与分页在后端执行
- “加载更多”：列表底部按钮；加载中禁用且展示旋转器

### 无障碍（a11y）
- 键盘：行容器支持 Enter/Space 展开；展开按钮具备 `aria-label`
- 角色语义：
  - List 形态：容器 `role="list"`，项 `role="listitem"`
  - Table 形态：容器 `role="grid"`，行 `role="row"`，单元格 `role="gridcell"`
- 排序（Table 形态）：列头使用 `aria-sort` 标注方向
- 焦点可见：遵循统一 outline 规范

### 响应式
- ≥1200px：完整布局
- 1024–1200px：列表全宽展示；与右侧面板并行时保证列表可读
- ≤1024px：行信息两行堆叠：
  - 第一行：`Date • Description`（Description 截断）
  - 第二行：左 `Accounts`，右 `Amount + Currency`
  - 操作图标靠右排列，保持 44×44 命中

### 虚拟化与性能
- 头部/行固定高度（60px）以稳定虚拟滚动；避免动态高度抖动
- 分组头 sticky；独立滚动区 `height: 100%; overflow-y: auto;`
- “加载更多”采用增量渲染与去抖，避免大批量 DOM 变更

### 设计 Token 对齐
- 颜色：`--color-primary-* / --color-tertiary-* / --color-error-* / --color-surface-*`
- 边框/分隔：`1px solid var(--color-surface-200)`
- 阴影：`--shadow-sm`/`--shadow-md`
- 字体：`--font-family-primary`；日期栏使用系统等宽字体族

示例映射（与 Tailwind 共存时建议迁移到 Token）：
```css
.txn-row { min-height: 60px; padding: 12px 16px; display: flex; align-items: center; border-bottom: 1px solid var(--color-surface-200); }
.txn-row:hover { background: var(--color-surface-50); }
.txn-date { width: 96px; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; color: var(--color-surface-600); }
.txn-desc { flex: 1 1 auto; min-width: 0; }
.txn-desc .truncate { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.txn-accounts { min-width: 200px; color: var(--color-surface-600); }
.txn-amount { min-width: 128px; text-align: right; font-weight: 600; color: var(--color-surface-900); }
.txn-amount.inflow { color: var(--color-tertiary-600); }
.txn-amount.outflow { color: var(--color-error-600); }
.txn-currency { width: 64px; text-align: right; letter-spacing: 0.02em; color: var(--color-surface-600); }
.txn-action { width: 44px; height: 44px; display: grid; place-items: center; border-radius: 9999px; }
.txn-action:focus { outline: 2px solid var(--color-primary-500); outline-offset: 2px; }

.month-header { position: sticky; top: 0; height: 60px; display: flex; align-items: center; padding: 0 16px; background: var(--color-surface-50); border-top: 1px solid var(--color-surface-200); border-bottom: 1px solid var(--color-surface-200); }
```

实现备注：
- 现有 `TransactionItem` 中金额配色逻辑与账户过滤规则保持不变；建议逐步将 `text-gray-*`/`bg-gray-*` 替换为 `--color-surface-*` 系列，以统一主题。
- 附件暂用新开页预览，后续可扩展为 Modal 预览（图片/PDF）。
- 行骨架占位（建议新增）：与 60px 行高对齐，含日期灰条、两段文本灰条与金额灰块。

---

## 🧱 Navigation Components (App v2-current)

### Left Sidebar（左侧边栏）
- 宽度：展开 280px；折叠 64px；右边框 `1px solid surface-300`；背景白。
- 品牌区：渐变品牌徽标（主/副渐变）、设置按钮 hover 强调。
- 账本选择器：渐变按钮（主/副渐变），加载态 spinner；下拉包含“Switch Ledger / Create New Ledger / Upload Ledger File”。
- 菜单项：图标 + 文本；`active` 使用品牌渐变背景，文字白色；`comingSoon` 显示徽记并禁用交互。
- 可展开子菜单：`expand-icon` 旋转 90° 表示展开；子项支持 `disabled`。
- 折叠态：仅显示图标；`active` 为方形渐变 tile（40×40）并加阴影。
- 焦点态：统一使用 `outline: 2px solid primary; outline-offset: 2px;`。

示例样式片段：
```css
.left-sidebar { background: #fff; border-right: 1px solid var(--color-surface-300); }
.project-selector { background: var(--gradient-primary); color: #fff; border-radius: 8px; }
.ledger-dropdown { background: #fff; border: 1px solid var(--color-surface-200); border-radius: 12px; box-shadow: var(--shadow-md3-3); }
.sidebar-menu-item.active { background: var(--gradient-primary); color: #fff; box-shadow: var(--shadow-md3-2); }
.coming-soon-badge { background: var(--color-surface-100); color: var(--color-surface-600); border: 1px solid var(--color-surface-300); }
```

### Middle Bar（中栏工具条）
- 宽度：60px；背景 `surface-50`，两侧半透明分隔线；竖直排列。
- 头像按钮：40×40，悬浮时文字从品牌色过渡到白色，带轻微抬升与光晕阴影。
- 图标按钮：36×36（建议升级至 44×44 以满足触控规范，见下文无障碍章节）。
- 通知红点：`notification-pulse` 动效（轻微缩放与透明度变化）。
- AI 触发器：44×44 渐变圆角按钮，悬浮时放大与加深阴影。

示例样式片段：
```css
.middle-bar { width: 60px; background: var(--color-surface-50); backdrop-filter: blur(8px); }
.notification-dot { width: 8px; height: 8px; background: var(--color-error-500); animation: notification-pulse 2s infinite; }
.ai-assistant-trigger { width: 44px; height: 44px; background: var(--gradient-primary); }
```

### Mobile Navigation（移动端导航）
- 顶部固定毛玻璃导航 `position: fixed; backdrop-filter: blur(10px);`。
- 下拉菜单带分区与激活态；`active` 使用品牌渐变；hover 使用主/副浅色渐变背景。
- 点击空白区域（容器外）关闭下拉。

示例样式片段：
```css
.mobile-nav { position: fixed; top: 0; left: 0; right: 0; background: rgba(255,255,255,.95); border-bottom: 1px solid var(--color-surface-200); }
.mobile-menu { position: absolute; top: 100%; left: 0; right: 0; box-shadow: var(--shadow-md); border-top: 1px solid var(--color-surface-200); }
.mobile-menu-item.active { background: var(--gradient-primary); color: #fff; }
```

---

## 🤖 AI Assistant Panel（右侧 AI 面板）

### 结构
- Header：标题 + 动作（新对话、历史、最大化、反馈、关闭），尺寸紧凑；hover 背景 `surface-100`。
- Chat：欢迎态（品牌图标、问候）、中部内容区自适应高度。
- Suggestions：建议卡片（白底、边框、hover 抬升）、快捷 Chips（圆角满角、边框、浅色悬浮）。
- Footer：固定底部输入区（absolute 定位），包含多行输入、发送按钮（禁用态半透明与灰度）。

### 关键规格
- 最小宽度：400px；桌面默认 500px 列宽。
- 输入聚焦：边框变 primary-400 并显示浅色内发光投影。
- 发送按钮：可用时带品牌边框，禁用态灰度与不可点击。

示例样式片段：
```css
.ai-panel { min-width: 400px; border-left: 1px solid var(--color-surface-300); display: flex; flex-direction: column; }
.ai-suggestions .suggestion-item { background: #fff; border: 1px solid var(--color-surface-200); box-shadow: var(--shadow-md3-1); }
.ai-input .input-container:focus-within { border-color: var(--color-primary-400); box-shadow: 0 0 0 3px rgba(25,118,210,.1); }
.send-icon.disabled { opacity: .5; pointer-events: none; filter: grayscale(20%); }
```

---

## 🎛️ Design Token 命名与工具类对齐

为与实现保持一致，规范 CSS 变量与工具类命名：

### 变量命名（规范）
```css
:root {
  /* 推荐统一前缀 color- */
  --color-primary-500: #1976d2;
  --color-secondary-500: #9c27b0;
  --color-tertiary-500: #009688;
  --color-error-500: #f44336;
  
  /* Surface 颜色系统 - 提升对比度 */
  --color-surface-50: #f8fafc;     /* 极浅灰 - hover背景 */
  --color-surface-100: #f1f5f9;    /* 浅灰 - 卡片背景 */
  --color-surface-200: #e2e8f0;    /* 边框颜色 */
  --color-surface-300: #cbd5e1;    /* 深边框、分隔线 */
  --color-surface-400: #64748b;    /* 图标颜色（提升对比度） */
  --color-surface-500: #475569;    /* 次要文字 */
  --color-surface-600: #374151;    /* 主要文字（辅助） */
  --color-surface-700: #1f2937;    /* 主要文字 */
  --color-surface-800: #111827;    /* 重要文字 */
  --color-surface-900: #030712;    /* 标题文字 */
}
```

### 工具类（示例）
```css
/* 文本颜色 - 使用适当的对比度 */
.text-surface-900 { color: var(--color-surface-900); }  /* 标题文字 (#030712) */
.text-surface-800 { color: var(--color-surface-800); }  /* 重要文字 (#111827) */
.text-surface-700 { color: var(--color-surface-700); }  /* 主要文字 (#1f2937) */
.text-surface-600 { color: var(--color-surface-600); }  /* 辅助文字 (#374151) */
.text-surface-500 { color: var(--color-surface-500); }  /* 次要文字 (#475569) */
.text-surface-400 { color: var(--color-surface-400); }  /* 图标颜色 (#64748b) */

/* 图标专用颜色类 */
.icon-default { color: var(--color-surface-400); }      /* 常规图标 */
.icon-secondary { color: var(--color-surface-500); }    /* 次要图标 */
.icon-important { color: var(--color-surface-600); }    /* 重要图标 */

/* 背景颜色 */
.bg-surface-50 { background-color: var(--color-surface-50); }    /* hover背景 */
.bg-surface-100 { background-color: var(--color-surface-100); }  /* 卡片背景 */

/* 边框颜色 */
.border-surface-200 { border-color: var(--color-surface-200); }  /* 边框 */
.border-surface-300 { border-color: var(--color-surface-300); }  /* 深边框 */

/* 渐变背景 */
.bg-gradient-primary { background: linear-gradient(135deg, var(--color-primary-500), var(--color-secondary-500)); }
```

### Surface 颜色使用指导

**文字颜色层级**：
- `surface-900`: 页面标题、卡片标题 (#030712)
- `surface-800`: 重要文字、主要内容 (#111827)
- `surface-700`: 常规文字、按钮文字 (#1f2937)
- `surface-600`: 辅助文字、说明文字 (#374151)
- `surface-500`: 次要文字、placeholder (#475569)
- `surface-400`: 图标颜色（提升后） (#64748b)

**背景与边框**：
- `surface-50`: hover状态背景
- `surface-100`: 卡片背景、输入框背景
- `surface-200`: 默认边框、分隔线
- `surface-300`: 强调边框、按钮边框

**图标颜色使用**：
- `surface-400` (#64748b): 常规图标、导航图标
- `surface-500` (#475569): 次要图标、禁用图标  
- `surface-600` (#374151): 重要图标、操作图标
- `primary-600`: 品牌图标、激活状态图标
- `error-600`: 错误/删除图标
- `tertiary-600`: 成功/确认图标

**对比度要求**：
- 主要文字：对比度 ≥ 7:1 (WCAG AAA)
- 辅助文字：对比度 ≥ 4.5:1 (WCAG AA)
- 图标：对比度 ≥ 4.5:1 (WCAG AA) - 提升标准
- 装饰性图标：对比度 ≥ 3:1 (WCAG AA)

说明：若历史文档处仍使用 `--surface-100` 等无前缀变量，请统一替换为 `--color-surface-100` 系列；工具类请显式包含色阶（如 `.bg-surface-100`）。

---

## 🌀 动效与状态映射

### 动效清单
```css
/* 下拉/弹出：用于账本菜单、移动菜单 */
@keyframes slideDown { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }

/* 状态指示：用于通知红点、AI 在线 */
@keyframes notification-pulse { 0%,100% { opacity: 1; transform: scale(1); } 50% { opacity: .7; transform: scale(1.1); } }

/* 悬浮抬升（统一） */
.hover-lift:hover { transform: translateY(-2px); box-shadow: var(--shadow-md3-2); }
```

### 使用建议
- 列表 hover、可点击卡片：使用 `hover-lift`，避免大位移。
- 菜单与下拉：使用 `slideDown` 200ms，减速曲线。
- 警示与在线状态：使用 `notification-pulse`，幅度轻微、节律缓和。
- Ripple：如无特别需要，不在新 UI 组件中默认启用。

---

## ♿ 无障碍与触控尺寸

- 触控最小尺寸：建议 44×44px。当前以下控件低于此尺寸，推荐后续统一调整或扩展可点区域：
  - 中栏图标按钮：36×36（建议 44×44）
  - 中栏头像：40×40（建议 44×44）
  - 侧边栏折叠按钮：40×40（建议 44×44）
- 焦点样式：统一 `outline: 2px solid var(--color-primary-500); outline-offset: 2px;`。
- 对比度：遵循正文 ≥ 4.5:1、大字/图标 ≥ 3:1；品牌渐变上文字需强制白色并校验对比度。

---

## 🗂️ 页面与组件网格说明

- 页面层：采用 12 列网格（参考前文 Grid System）。
- 组件层：按场景选用 2/3/4 列（如仪表盘统计卡 4 列），在断点处退化为 2 列和 1 列。
- 说明：页面层网格负责整体布局约束；组件层网格保证局部一致性与可读性。

---

## 📝 Changelog

### 1.1.1 — 2025-09-15
- 修复：统一响应式断点为 1024px (Tailwind lg)，与移动导航断点保持一致
- 更新：Workspace Layout 和 Transactions List 响应式规范中的断点值

### 1.1 — 2025-09-14
- 新增：Workspace Layout（桌面/响应式列宽与行为）
- 新增：Navigation Components（左侧边栏 / 中栏 / 移动端导航）
- 新增：AI Assistant Panel 规范（结构、状态与最小宽度）
- 新增：Design Token 命名与工具类对齐（统一 --color- 前缀与类名）
- 新增：动效映射（slideDown、notification-pulse、hover-lift）
- 新增：无障碍触控尺寸建议与差异清单
- 新增：页面层 vs 组件层网格使用说明
- 新增：Transactions List（数据表）规范（分组/虚拟化/交互）
