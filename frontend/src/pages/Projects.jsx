import { motion, useScroll, useTransform } from "framer-motion";
import { useState, useRef, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { projects } from "../data/projects";
import { FaWhatsapp } from "react-icons/fa";
import { Building2, ShieldCheck, Star, KeyRound } from "lucide-react";
import Footer from "../components/Footer";
import Map from "../components/Map";

const Projects = () => {
  const { projectId } = useParams();
  const project = projects.find((p) => p.id === projectId);

  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  const imageRef = useRef(null);
  const { scrollY } = useScroll();
  const imageY = useTransform(scrollY, [0, 300], [0, -100]);

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [menuOpen, setMenuOpen] = useState(false);

  if (!project) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-black text-white">
        <div className="text-center">
          <h1 className="text-4xl font-bold mb-4">Property Not Found</h1>
          <Link to="/" className="text-blue-500 hover:underline">
            Return to Home
          </Link>
        </div>
      </div>
    );
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch("http://localhost:5000/customers", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, email, phone, project_id: projectId }),
      });

      const data = await response.json();
      if (!response.ok) {
        console.error("Error submitting form:", data.error);
        return;
      }

      console.log("Form submitted:", data);
      setName("");
      setEmail("");
      setPhone("");
    } catch (err) {
      console.error("Failed to submit form:", err);
    }
  };

  return (
    <div className="bg-black text-white min-h-screen">
      {/* Header */}
      <header className="w-full py-6 px-6 border-b border-white/10 relative z-30">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <div className="bg-orange-700 w-12 h-12 flex items-center justify-center rounded-lg">
              <Building2 className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-2xl font-bold">WH Realtors</h1>
          </div>

          {/* Desktop nav */}
          <nav className="hidden md:flex gap-6 text-sm font-medium text-white/90">
            <a href="#about-project" className="hover:text-orange-400">
              About
            </a>
            <a href="#gallery" className="hover:text-orange-400">
              Gallery
            </a>
            <a href="#features" className="hover:text-orange-400">
              Features
            </a>
            <a href="#contact" className="hover:text-orange-400">
              Contact
            </a>
          </nav>

          {/* Mobile menu button */}
          <button
            className="md:hidden text-white z-40"
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
                d={menuOpen ? "M6 18L18 6M6 6l12 12" : "M4 6h16M4 12h16M4 18h16"}
              />
            </svg>
          </button>
        </div>

        {/* Mobile dropdown menu */}
        {menuOpen && (
          <div className="md:hidden px-6 mt-2 space-y-2 bg-black/90 pb-4 absolute top-full left-0 w-full z-40">
            <a href="#about-project" className="block text-white hover:text-orange-400">
              About
            </a>
            <a href="#gallery" className="block text-white hover:text-orange-400">
              Gallery
            </a>
            <a href="#features" className="block text-white hover:text-orange-400">
              Features
            </a>
            <a href="#contact" className="block text-white hover:text-orange-400">
              Contact
            </a>
          </div>
        )}
      </header>

      {/* Hero Title */}
      <section className="text-center pt-20 pb-10 relative z-10">
        <h2 className="text-5xl md:text-6xl font-extrabold">{project.title}</h2>
        <a
          href={`https://wa.me/${project.whatsapp || "910000000000"}`}
          target="_blank"
          rel="noreferrer"
          className="inline-block mt-6 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-full text-lg font-medium"
        >
          <div className="flex items-center space-x-2">
            <FaWhatsapp className="text-lg" />
            <span>Book Now</span>
          </div>
        </a>
      </section>

      {/* Hero Image Parallax */}
      <motion.div
        ref={imageRef}
        style={{ y: imageY, zIndex: 20 }}
        className="relative z-20 overflow-hidden rounded-t-3xl w-screen max-w-7xl mx-auto"
      >
        <img
          src={project.image}
          alt={project.title}
          className="w-full object-cover rounded-t-3xl"
        />
      </motion.div>

      {/* About Project */}
      <section id="about-project" className="bg-black py-16 px-6">
        <div className="max-w-6xl mx-auto">
          <motion.h3
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
            className="text-4xl font-bold mb-8"
          >
            About Project
          </motion.h3>
          <p className="text-xl text-gray-300 max-w-4xl mb-12">{project.description}</p>
          <div className="grid md:grid-cols-3 gap-6">
            {project.Advantages.map((adv, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: i * 0.2 }}
                viewport={{ once: true }}
                className="bg-white/5 p-6 rounded-2xl text-white text-center shadow-md"
              >
                <div className="text-blue-500 mb-4">
                  {i % 3 === 0 ? (
                    <ShieldCheck className="mx-auto w-8 h-8" />
                  ) : i % 3 === 1 ? (
                    <Star className="mx-auto w-8 h-8" />
                  ) : (
                    <KeyRound className="mx-auto w-8 h-8" />
                  )}
                </div>
                <h4 className="text-xl font-bold mb-2">{adv.title || "Feature"}</h4>
                <p className="text-sm text-gray-300">{adv.desc || adv}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Gallery Section - Horizontal scroll */}
      <section id="gallery" className="max-w-6xl mx-auto px-6 pb-16 relative z-10">
        <h3 className="text-4xl font-semibold mb-10 text-center">Project Gallery</h3>
        <div className="flex gap-4 overflow-x-auto md:grid md:grid-cols-2 md:gap-6 scrollbar-hide">
          {Object.entries(project.galleryCovers || {}).map(([cat, src]) => (
            <div
              key={cat}
              className="min-w-[300px] md:min-w-0 rounded-2xl overflow-hidden"
            >
              <img
                src={src}
                alt={cat}
                className="w-full object-cover rounded-2xl h-64 md:h-auto"
              />
            </div>
          ))}
        </div>
      </section>

      {/* Property Features - Horizontal scroll */}
      <section id="features" className="bg-black py-16 px-6">
        <div className="max-w-6xl mx-auto">
          <h3 className="text-4xl font-bold text-center mb-12">Property Features</h3>
          <div className="flex gap-4 overflow-x-auto md:grid md:grid-cols-3 md:gap-6 scrollbar-hide">
            {project.features.map((feature, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: idx * 0.1 }}
                viewport={{ once: true }}
                className="min-w-[300px] md:min-w-0 bg-white/5 p-6 rounded-2xl shadow-md text-center text-white"
              >
                <div className="text-blue-400 mb-4">
                  <ShieldCheck className="mx-auto w-8 h-8" />
                </div>
                <h4 className="text-xl font-semibold mb-2">
                  {feature.title || feature}
                </h4>
                <p className="text-sm text-gray-300">
                  {feature.desc ||
                    "24x7 Security of your Property Residence and the society with surveillance of world standards."}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Contact Section */}
      <section id="contact" className="bg-black px-6 py-16">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row gap-8 items-start">
          <div className="w-full md:w-1/2">
            <Map projectTitle={project.title} />
          </div>
          <div className="w-full md:w-1/2">
            <h3 className="text-3xl font-bold mb-6">Get In Touch</h3>
            <form className="space-y-4" onSubmit={handleSubmit}>
              <div>
                <label className="block mb-1 text-sm">Name</label>
                <input
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full px-4 py-2 rounded bg-gray-800 text-white"
                  placeholder="Jane Smith"
                  required
                />
              </div>
              <div>
                <label className="block mb-1 text-sm">Email</label>
                <input
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-4 py-2 rounded bg-gray-800 text-white"
                  placeholder="jane@framer.com"
                  required
                />
              </div>
              <div>
                <label className="block mb-1 text-sm">Phone</label>
                <input
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  className="w-full px-4 py-2 rounded bg-gray-800 text-white"
                  placeholder="+91 00000 00000"
                />
              </div>
              <button
                type="submit"
                className="w-full px-6 py-2 bg-gray-700 hover:bg-gray-600 rounded text-white font-medium"
              >
                Submit
              </button>
            </form>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
};

export default Projects;
