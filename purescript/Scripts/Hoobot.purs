module Scripts.Hoobot (script) where

import Prelude
import Control.Monad.Aff (Aff, launchAff)
import Control.Monad.Eff (Eff)
import Control.Monad.Eff.Class (liftEff)
import Control.Monad.Eff.Console (CONSOLE, log)
import Control.Monad.Eff.Exception (EXCEPTION)
import Data.Argonaut.Core (Json)
import Data.Argonaut.Decode.Combinators ((.?))
import Data.Argonaut.Decode.Class (class DecodeJson, decodeJson)
import Data.Argonaut.Parser (jsonParser)
import Data.Either (Either(..))
import Data.Maybe (Maybe(..))
import Data.Options ((:=))
import Data.String.Regex (Regex, noFlags, regex)
import Data.String.Yarn (unlines)
import Node.HTTP (HTTP)
import Node.HTTP.ScopedClient (get)

import Hubot (HUBOT, Robot, hear, http, match, send)

hoogleURL :: String -> String
hoogleURL str = "https://www.haskell.org/hoogle/?mode=json&hoogle=" <> str <> "&start=0&count=10"

newtype HoogleResult = HoogleResult { url :: String, typeSig :: String }

instance decodeHoogleResult :: DecodeJson HoogleResult where
    decodeJson json = do
        obj <- decodeJson json
        url <- obj .? "location"
        typeSig <- obj .? "self"
        pure $ HoogleResult { url, typeSig }

showHoogleResult :: HoogleResult -> String
showHoogleResult (HoogleResult res) = res.typeSig <> " <" <> res.url <> "|link>"

parseHoogleResults :: Json -> Either String (Array HoogleResult)
parseHoogleResults json = do
    obj <- decodeJson json
    obj .? "results"

script' :: forall e. Robot -> Regex -> Aff (http :: HTTP, hubot :: HUBOT | e) Unit
script' robot pat = do
    response <- hear pat robot
    case match response 1 of
        Just str -> do
            client <- liftEff $ http (hoogleURL str) robot
            result <- get client
            let message = case jsonParser result.body >>= parseHoogleResults of
                    Left err -> err
                    Right results -> unlines $ map showHoogleResult results
            liftEff $ send message response 
        Nothing -> pure unit
    
script :: Robot -> Eff (err :: EXCEPTION, http :: HTTP, hubot :: HUBOT, console :: CONSOLE) Unit
script robot = case regex "!hoogle (.*)$" noFlags of
    Left err -> log err
    Right pat -> do
        launchAff $ script' robot pat
        pure unit
