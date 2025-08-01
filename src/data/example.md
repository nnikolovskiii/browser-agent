Here is a plan to refactor the homepage (`AboutMePage.tsx`) to adopt the styling and layout of the blog posts page (`BlogPostsPage.tsx`).

The core idea is to replace the unique layout of the `AboutMePage` with the shared layout components used by `BlogPostsPage`, ensuring a consistent look and feel across the application. The "About Me" content will be placed within this new, consistent structure.

### 1. Extract "About Me" Content into a Reusable Component

The first step is to isolate the content of the "About Me" page from its current layout.

*   **Create a new directory:** `frontend/src/components/AboutMe/`
*   **Create a new file:** `frontend/src/components/AboutMe/AboutMeContent.tsx`
*   **Action:** Move the JSX from the `<main>` element in `frontend/src/pages/AboutMePage.tsx` into this new `AboutMeContent.tsx` component. This includes the hero section, text, buttons, and image. Also, move the `handleImageError` function.
*   **Action:** The root element of this new component should be a `div` that fills the available space and allows scrolling, similar to how `BlogPostDetail.tsx` is structured.

**`frontend/src/components/AboutMe/AboutMeContent.tsx` (New File)**
```tsx
import React from 'react';

const AboutMeContent: React.FC = () => {
    // Typed event handler for the image's onError event
    const handleImageError = (e: React.SyntheticEvent<HTMLImageElement, Event>) => {
        e.currentTarget.src = 'https://placehold.co/300x300/EFEFEF/333333?text=NN';
        e.currentTarget.alt = 'Placeholder image for Nikola Nikolovski';
    };

    return (
        <main className="flex-1 p-8 overflow-y-auto bg-gray-50">
            <div className="container mx-auto max-w-6xl">
                <div className="flex flex-col md:flex-row items-center justify-between">
                    {/* Left Section: Text Content */}
                    <div className="w-full md:w-1/2 text-center md:text-left mb-12 md:mb-0">
                        <span className="text-sky-700 font-bold text-lg uppercase tracking-wider">
                            Nikola Nikolovski
                        </span>
                        <h1 className="text-5xl md:text-7xl font-bold text-gray-800 my-2 leading-tight">
                            AI Software <span className="text-sky-700">Engineer</span>
                        </h1>
                        <p className="text-xl text-gray-600 mt-4 mb-8 leading-relaxed">
                            Developing intelligent applications and leveraging AI to solve real-world problems.
                        </p>
                        <div className="flex justify-center md:justify-start space-x-4">
                            <button className="bg-sky-700 hover:bg-sky-800 text-white font-bold py-3 px-8 rounded-lg shadow-lg transition-transform transform hover:scale-105">
                                Portfolio
                            </button>
                            <button className="bg-white text-sky-700 border-2 border-sky-600 font-bold py-3 px-8 rounded-lg shadow-lg transition-transform transform hover:scale-105 hover:bg-sky-50">
                                Contact
                            </button>
                        </div>

                        {/* Social Links */}
                        <div className="mt-8 flex justify-center md:justify-start space-x-6">
                            {/* ... (SVG icons remain here) ... */}
                        </div>
                    </div>

                    {/* Right Section: Image and Decorative Elements */}
                    <div className="w-full md:w-1/2 flex items-center justify-center mt-10 md:mt-0">
                        <div className="relative w-96 h-96">
                            {/* ... (Decorative elements and profile image remain here) ... */}
                             <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-72 h-72 rounded-full overflow-hidden shadow-2xl z-10 border-4 border-white">
                                <img
                                    src="http://nnikkserver.duckdns.org:5001/test/download/nnikola-removebg-preview.png"
                                    alt="Nikola Nikolovski, AI Software Engineer"
                                    className="w-full h-full object-cover"
                                    onError={handleImageError}
                                />
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    );
};

export default AboutMeContent;
```

### 2. Update the Homepage to Use the Blog Layout

Now, overhaul `AboutMePage.tsx` to use the same layout components as `BlogPostsPage.tsx`.

*   **Modify file:** `frontend/src/pages/AboutMePage.tsx`
*   **Action:** Replace the entire content of the file with a new structure that imports and uses `Header`, `Sidebar`, and the new `AboutMeContent` component. It will need its own state to manage the sidebar.

**`frontend/src/pages/AboutMePage.tsx` (Modified)**
```tsx
import { useState } from 'react';
import { Header, Sidebar } from '../components/BlogPosts/layout';
import AboutMeContent from '../components/AboutMe/AboutMeContent';
import styles from './BlogPostsPage.module.css'; // Reuse the same CSS module for consistency

export default function AboutMePage() {
    const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
    
    // These states are needed for the Sidebar component props, even if not fully used on this page.
    const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

    const toggleSidebar = () => {
        setIsSidebarCollapsed(!isSidebarCollapsed);
    };

    // The Sidebar component expects this prop, so we provide a dummy function.
    const setSelectedPost = () => {};

    return (
        <div className={`${styles.blogPostPage} bg-white min-h-screen text-gray-800 font-sans`}>
            <Header
                toggleSidebar={toggleSidebar}
                isSidebarCollapsed={isSidebarCollapsed}
            />
            <div className="flex">
                <Sidebar 
                    isSidebarCollapsed={isSidebarCollapsed} 
                    selectedCategory={selectedCategory}
                    setSelectedCategory={setSelectedCategory}
                    setSelectedPost={setSelectedPost}
                />
                <AboutMeContent />
            </div>
        </div>
    );
}
```

### 3. Deprecate the Old Header

The `AboutMeHeader.tsx` component is now redundant and should be removed to avoid confusion and code rot.

*   **Delete file:** `frontend/src/components/BlogPosts/layout/AboutMeHeader.tsx`

### 4. Consolidate Navigation (Optional but Recommended)

The old `AboutMeHeader` contained primary navigation links ("About", "Portfolio", "Blogs", "Contact"). The new, shared `Header` does not. A good user experience requires these links to be accessible. The `Sidebar` is the ideal place for them.

*   **Modify file:** `frontend/src/components/BlogPosts/layout/Sidebar.tsx` (This file was not provided, but the change would look like this)
*   **Action:** Add a navigation section at the top of the sidebar for the main pages of the site.

**Hypothetical `frontend/src/components/BlogPosts/layout/Sidebar.tsx` Modification**
```tsx
// ... imports
import { Link } from 'react-router-dom'; // Assuming you use react-router-dom for navigation

// ... interface

const Sidebar: React.FC<SidebarProps> = ({ /* ...props */ }) => {
    // ... existing state and hooks (like fetching categories)

    return (
        <aside className={/* ... dynamic classes for collapsing */}>
            <div className="p-4">
                {/* START: New Navigation Section */}
                <nav className="mb-6 pb-6 border-b border-gray-200">
                    <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">Menu</h3>
                    <ul>
                        <li>
                            <Link to="/" className="flex items-center p-2 rounded-md hover:bg-gray-100 font-medium">
                                About Me
                            </Link>
                        </li>
                        <li>
                            <Link to="/portfolio" className="flex items-center p-2 rounded-md hover:bg-gray-100 font-medium">
                                Portfolio
                            </Link>
                        </li>
                        <li>
                            <Link to="/blogs" className="flex items-center p-2 rounded-md hover:bg-gray-100 font-medium">
                                Blogs
                            </Link>
                        </li>
                    </ul>
                </nav>
                {/* END: New Navigation Section */}

                {/* Existing Categories Section */}
                <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">Categories</h3>
                {/* ... existing logic to map and display categories */}
            </div>
        </aside>
    );
};

export default Sidebar;
```

This plan standardizes your application's layout, improves code reusability, and provides a more consistent user experience between the homepage and the blog section.