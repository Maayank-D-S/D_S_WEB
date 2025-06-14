import { useState } from "react";
import { motion, useScroll, useTransform } from "framer-motion";
import { Building2 } from "lucide-react";
import { projects } from "../data/projects";
import ProjectCard from "../components/ProjectCard";
import Footer from "../components/Footer";
import Chat from "../components/Chat";

const team = [
  { name: "John Doe", role: "CEO", image: "/team1.png" },
  { name: "Jane Smith", role: "CTO", image: "/team2.png" },
  { name: "David Lee", role: "COO", image: "/team3.png" },
  { name: "Ava Taylor", role: "CMO", image: "/team4.png" },
];

const Landing = () => {
  const { scrollY } = useScroll();
  const videoY = useTransform(scrollY, [0, 300], [0, -100]);
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <div className="min-h-screen bg-black text-white overflow-x-hidden">
      {/* ────────── HERO ────────── */}
      <div className="relative h-[100vh] overflow-hidden">
        {/* Background video */}
        <motion.div
          style={{ y: videoY }}
          className="h-[100vh] absolute top-0 left-0 w-full z-10 overflow-hidden"
        >
          <video
            autoPlay
            muted
            loop
            playsInline
            className="w-full h-full object-cover"
          >
            <source src="/video.mp4" type="video/mp4" />
          </video>
        </motion.div>

        {/* Header */}
        <div className="relative w-full h-24 py-6 bg-black/70 z-30">
          <div className="container mx-auto px-6 flex items-center justify-between h-full">
            {/* Logo */}
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 rounded-lg flex items-center justify-center">
                <img src="/logo.png" alt="" className="h-10 w-10" />
              </div>
              <h1 className="text-2xl font-bold">WH&nbsp;Realtors</h1>
            </div>

            {/* Desktop nav */}
            <nav className="hidden md:flex space-x-8 text-lg">
              <a href="#discover" className="hover:text-orange-400">
                Discover
              </a>
              <a href="#gallery" className="hover:text-orange-400">
                Gallery
              </a>
              <a href="#about" className="hover:text-orange-400">
                About
              </a>
              <a href="#contact" className="hover:text-orange-400">
                Contact
              </a>
            </nav>

            {/* Mobile menu button */}
            <button
              className="md:hidden text-white focus:outline-none z-40"
              onClick={() => setMenuOpen(!menuOpen)}
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-8 w-8"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d={
                    menuOpen
                      ? "M6 18L18 6M6 6l12 12"
                      : "M4 6h16M4 12h16M4 18h16"
                  }
                />
              </svg>
            </button>
          </div>

          {/* Mobile dropdown */}
          {menuOpen && (
            <div className="md:hidden px-6 mt-2 space-y-2 bg-black/90 pb-4 z-40 absolute top-full left-0 w-full">
              <a
                href="#discover"
                className="block text-white hover:text-orange-400"
              >
                Discover
              </a>
              <a
                href="#gallery"
                className="block text-white hover:text-orange-400"
              >
                Gallery
              </a>
              <a
                href="#about"
                className="block text-white hover:text-orange-400"
              >
                About
              </a>
              <a
                href="#contact"
                className="block text-white hover:text-orange-400"
              >
                Contact
              </a>
            </div>
          )}
        </div>

        {/* Hero Content */}
        <div className="relative z-20 flex items-center justify-center h-[calc(100vh-96px)] px-6">
          <div className="text-center max-w-3xl">
            <motion.h2
              initial={{ opacity: 0, y: 40 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              className="text-5xl md:text-7xl font-extrabold mb-4"
            >
              Elevate&nbsp;Your&nbsp;Living
            </motion.h2>
            <motion.p
              initial={{ opacity: 0, y: 40 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 1.2 }}
              className="text-xl md:text-2xl text-gray-300"
            >
              Discover the most exclusive properties with WH&nbsp;Realtors.
            </motion.p>
          </div>
        </div>
      </div>

      {/* ────────── DESCRIPTION ────────── */}
      <section className="py-20 px-6 bg-black">
        <div className="container mx-auto max-w-7xl">
          <div className="bg-[#111] rounded-2xl flex flex-col md:flex-row items-center justify-between p-8 md:p-12 gap-6">
            {/* Text Content */}
            <div className="flex-1">
              <h2 className="text-3xl md:text-4xl font-extrabold mb-4">
                We are <span className="text-white">WH Realtors</span>
              </h2>
              <p className="text-lg text-gray-300 mb-2 font-medium">
                We are the Developers of Tomorrow.
              </p>
              <p className="text-sm text-gray-400 mb-4">
                At Wild Habitat, we’re reimagining what it means to build. We're
                not just real estate developers — we're engineers,
                technologists, and designers on a mission to transform how real
                estate is created, sold, and experienced. Our model is rooted in
                deep technology, clean execution, and absolute transparency.
                From how our projects are designed and built to how they're
                marketed and sold — everything is powered by in-house AI and
                automation systems.
              </p>
              <p className="text-sm text-gray-400">
                Backed by a strong engineering foundation (IIT alumni) and a
                relentless focus on innovation, we’re pioneering a new era of
                real estate development where speed, trust, and precision define
                the experience.
              </p>
            </div>

            {/* Logo */}
            <div className="w-28 md:w-40 flex-shrink-0">
              <img
                src="/logo.png"
                alt="WH Realtors Logo"
                className="w-full h-auto object-contain"
              />
            </div>
          </div>
        </div>
      </section>
      <section id="discover" className="py-20 px-6 bg-black">
        <div className="container mx-auto max-w-6xl text-center">
          <h2 className="text-4xl font-bold mb-6">
            Your Trusted Real Estate Partner
          </h2>
          <p className="text-lg text-gray-400 max-w-3xl mx-auto mb-12">
            At WH&nbsp;Realtors, we create exceptional residential and
            commercial properties that elevate lifestyles.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              {
                iconColor: "bg-blue-500",
                label: "Quality Construction",
                desc: "Top-tier materials and workmanship in every build.",
              },
              {
                iconColor: "bg-green-500",
                label: "Prime Locations",
                desc: "Properties strategically placed for convenience and value.",
              },
              {
                iconColor: "bg-purple-500",
                label: "Customer First",
                desc: "Personalized service and end-to-end support.",
              },
            ].map((f, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 40 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.2, duration: 0.6 }}
                viewport={{ once: true }}
                className="bg-white/5 rounded-xl p-6 shadow-lg text-left"
              >
                <div
                  className={`w-12 h-12 ${f.iconColor} rounded-lg flex items-center justify-center mb-4`}
                >
                  <Building2 className="w-5 h-5 text-white" />
                </div>
                <h3 className="text-xl font-semibold mb-2">{f.label}</h3>
                <p className="text-gray-400 text-sm">{f.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ────────── GALLERY ────────── */}
      <section id="gallery" className="py-20 px-6 bg-black">
        <div className="container mx-auto">
          <h2 className="text-4xl font-bold text-center mb-12">
            Featured Properties
          </h2>
          <div className="flex gap-6 overflow-x-auto md:grid md:grid-cols-2 lg:grid-cols-3 md:gap-8 scrollbar-hide">
            {projects.map((p) => (
              <div key={p.id} className="min-w-[320px] md:min-w-0">
                <ProjectCard project={p} />
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ────────── ABOUT US ────────── */}
      <section id="about" className="py-20 px-6 bg-black">
        <div className="container mx-auto">
          <h2 className="text-4xl font-bold mb-6">About Us</h2>
          <p className="text-gray-300 mb-10 max-w-4xl">
            We are WH Realtors, passionate about shaping premium living
            experiences...
          </p>
          <div className="flex space-x-6 overflow-x-auto pb-4 scrollbar-hide">
            {team.map((member, index) => (
              <div
                key={index}
                className="flex-shrink-0 w-64 bg-white/5 rounded-2xl p-4 text-center"
              >
                <img
                  src={member.image}
                  alt={member.name}
                  className="rounded-xl w-full h-72 object-cover mb-4"
                />
                <h4 className="text-lg font-semibold">{member.name}</h4>
                <p className="text-sm text-gray-400">{member.role}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ────────── CONTACT ────────── */}
      <section id="contact" className="py-20 px-6 bg-black">
        <div className="container mx-auto max-w-2xl text-center">
          <h2 className="text-4xl font-bold mb-6">Get In Touch</h2>
          <form className="space-y-6 text-left">
            {["Name", "Email", "Location"].map((label, i) => (
              <div key={i}>
                <label className="block mb-1 text-sm text-gray-300">
                  {label}
                </label>
                <input
                  type="text"
                  placeholder={`Enter your ${label.toLowerCase()}`}
                  className="w-full px-4 py-3 rounded-md bg-white/5 border border-gray-700 text-white focus:outline-none"
                />
              </div>
            ))}
            <button
              type="submit"
              className="w-full bg-white/5 text-white py-3 rounded-md font-semibold hover:bg-gray-200"
            >
              Submit
            </button>
          </form>
        </div>
      </section>

      <Footer />
      <Chat />
    </div>
  );
};

export default Landing;
