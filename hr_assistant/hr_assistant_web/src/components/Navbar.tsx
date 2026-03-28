import React, { useState } from "react";
import { Link, NavLink } from "react-router-dom";
import { Users, MessageSquare, Menu, X, Briefcase } from "lucide-react";

const Navbar: React.FC = () => {
  const [mobileOpen, setMobileOpen] = useState(false);

  const navItems = [
    { to: "/employees", label: "Employees", icon: <Users className="w-4 h-4" /> },
    { to: "/chat", label: "Chat", icon: <MessageSquare className="w-4 h-4" /> },
  ];

  const linkClass = (active: boolean) =>
    [
      "flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors",
      active
        ? "bg-primary-700 text-white"
        : "text-primary-100 hover:bg-primary-700 hover:text-white",
    ].join(" ");

  return (
    <nav className="bg-primary-600 shadow-md">
      <div className="container mx-auto px-4 max-w-7xl">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 text-white font-bold text-lg">
            <Briefcase className="w-6 h-6" />
            HR Assistant
          </Link>

          {/* Desktop nav */}
          <div className="hidden md:flex items-center gap-1">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) => linkClass(isActive)}
              >
                {item.icon}
                {item.label}
              </NavLink>
            ))}
          </div>

          {/* Mobile hamburger */}
          <button
            className="md:hidden text-white p-2 rounded-md hover:bg-primary-700"
            onClick={() => setMobileOpen((prev) => !prev)}
            aria-label="Toggle navigation menu"
          >
            {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      {mobileOpen && (
        <div className="md:hidden border-t border-primary-500 px-4 py-2 space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) => linkClass(isActive) + " w-full"}
              onClick={() => setMobileOpen(false)}
            >
              {item.icon}
              {item.label}
            </NavLink>
          ))}
        </div>
      )}
    </nav>
  );
};

export default Navbar;
