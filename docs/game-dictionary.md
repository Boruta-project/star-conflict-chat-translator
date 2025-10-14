# Star Conflict Game Dictionary

<div align="center">
  <h1>🎮 Community Game Dictionary</h1>
  <p><em>Help improve translations with game-specific terms and phrases</em></p>
</div>

## 📖 Overview

The **Star Conflict Game Dictionary** is a community-maintained collection of game-specific terms, phrases, and translations that help improve the accuracy of chat message translations. While the application uses Google Translate for general language translation, this dictionary provides specialized translations for:

- **Ship names and classes** (Tornado, Mammoth, Kusarigama)
- **Weapon and equipment names** (Plasma Gun, Tai'thaq 17)
- **Game-specific terminology** (spec ops, xpam, CNC)
- **Faction and location names**
- **Common gaming phrases and slang**

## 📁 Dictionary Location

The community dictionary is located at:
```
📂 game_dictionary.json (root directory)
```

This placement ensures:
- **Easy access** for contributors
- **Version control** through Git
- **Automatic updates** for users
- **Community collaboration** via GitHub

## 🤝 How to Contribute

### Method 1: Direct GitHub Edit (Recommended)

1. **Navigate** to `game_dictionary.json` in the repository
2. **Click** the pencil icon (Edit this file)
3. **Add** your translation entries
4. **Create** a pull request with your changes

### Method 2: Issue Report

1. **Create** a new [Issue](../../issues/new) with title: "Dictionary: Add [term]"
2. **Provide** the term, translation, and context
3. **Use** the format:
   ```json
   "original_term": "translated_term"
   ```

### Method 3: Local Development

1. **Fork** the repository
2. **Clone** your fork locally
3. **Edit** `game_dictionary.json`
4. **Test** your changes
5. **Submit** a pull request

## 📝 Contribution Guidelines

### Entry Format
```json
{
  "game_term": "translated_term",
  "another_term": "another_translation"
}
```

### Quality Standards
- ✅ **Accurate translations** - Verify translations are correct
- ✅ **Context appropriate** - Consider gaming context
- ✅ **Consistent formatting** - Follow existing patterns
- ✅ **No duplicates** - Check if term already exists
- ✅ **Test entries** - Verify they work in-game

### Categories of Terms to Add

#### 🚀 Ship Names & Classes
```json
"[Link 2 D: Ship_race3_m_t5_craftuniq]": "[Tornado]",
"[Link 2 D: Ship_race3_L_T5_PREMIUM]": "[Mammoth]",
"[link 11 d:Ship_Race2_S_T5_Uniq_part]": "[Special part of the ship "Kusarigama"]"
```

#### ⚔️ Weapons & Equipment
```json
"[link 1 d:Weapon_CorrosiveGun_T5_Rel]": "[Tai'thaq 17]",
"[link 1 d:Weapon_Corrosivegun_T5_Rel]": "[Tai'thaq 17]"
```

#### 🎯 Game Terminology
```json
"xpam": "temple",
"cnc": "thank you",
"co+": "spec ops +",
"со+": "spec ops+"
```

#### 📦 Resources & Items
```json
"[link 11 d:Relics_craft_part]": "[Synthetic polycrystal]",
"[link 11 d:pve_resource]": "[Insignia]"
```

## 🔍 Finding Terms to Translate

### In-Game Sources
- **Chat messages** that translate poorly
- **Item descriptions** with technical terms
- **Ship and weapon names**
- **Faction-specific terminology**
- **Common abbreviations and slang**

### Testing Your Contributions
1. **Add** the term to your local dictionary
2. **Restart** the translator application
3. **Test** in-game with relevant chat messages
4. **Verify** the translation improves

## 🎯 Impact of Contributions

Your dictionary contributions help:
- **Improve translation accuracy** for all players
- **Reduce confusion** in international gameplay
- **Enhance communication** during battles and trading
- **Build community knowledge** of game terminology

## 🙏 Recognition

Contributors to the game dictionary are:
- ✅ **Listed** in CHANGELOG.md updates
- ✅ **Recognized** in release notes
- ✅ **Credited** in the application (future feature)
- ✅ **Invited** to contributor discussions

## 📞 Need Help?

- **Questions?** Create a [Discussion](../../discussions)
- **Issues?** Report via [Issues](../../issues)
- **Suggestions?** Start a [Discussion](../../discussions)

---

<div align="center">

**🌍 Help make Star Conflict more accessible to players worldwide! 🌍**

*Every translation improves the gaming experience for the international community.*

[📝 Contribute Now](../../edit/main/game_dictionary.json) • [🐛 Report Issues](../../issues) • [💬 Discuss](../../discussions)

</div>
